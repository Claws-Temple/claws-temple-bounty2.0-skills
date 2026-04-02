#!/usr/bin/env python3
"""High-level Task 3 executor for the Claws Temple faction oath flow.

This helper collapses the multi-step CA-only oath path into one stable entrypoint
that weaker agents can call with minimal orchestration.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import selectors
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.parse import quote
from zoneinfo import ZoneInfo

DEFAULT_NETWORK = "mainnet"
DEFAULT_RETRY_BACKOFFS = (3, 8, 15)
DEFAULT_RUNNER_TIMEOUT_SECONDS = 30.0
DEFAULT_JSON_GRACE_SECONDS = 0.2
STATUS_PASSWORD_REQUIRED = "password_required"
STATUS_WAITING_FOR_TOKENS = "waiting_for_tokens"
STATUS_BLOCKED = "blocked"
STATUS_COMPLETED = "completed"
STATUS_SUBMITTED = "submitted"
NON_BLOCKING_EXIT_STATUSES = {
    STATUS_COMPLETED,
    STATUS_PASSWORD_REQUIRED,
    STATUS_WAITING_FOR_TOKENS,
    STATUS_SUBMITTED,
}
PASSWORD_ERROR_MARKERS = (
    "password may be incorrect",
    "failed to decrypt keystore",
    "failed to decrypt active ca keystore",
)
TERMINAL_TX_FAILURE_STATUSES = {
    "FAILED",
    "NODEVALIDATIONFAILED",
    "REJECTED",
    "CANCELED",
    "CANCELLED",
}


class CommandExecutionError(RuntimeError):
    """Raised when a shell command exits non-zero or emits invalid JSON."""

    def __init__(self, command: Sequence[str], returncode: int, stdout: str, stderr: str) -> None:
        self.command = list(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        message = stderr.strip() or stdout.strip() or f"command failed with exit code {returncode}"
        super().__init__(message)


class ToolResponseError(RuntimeError):
    """Raised when a dependency tool returns a structured failure payload."""

    def __init__(self, label: str, payload: dict[str, Any]) -> None:
        self.label = label
        self.payload = payload
        message = payload.get("error", {}).get("message") or payload.get("message") or f"{label} returned an error"
        super().__init__(str(message))


class EarlyResult(Exception):
    """Raised to exit the executor with a machine-readable payload."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        super().__init__(payload.get("summary", "executor exited early"))


class JsonRunner:
    """Thin shell runner that expects JSON on stdout."""

    def __init__(
        self,
        *,
        overall_timeout_seconds: float | None = None,
        post_json_grace_seconds: float = DEFAULT_JSON_GRACE_SECONDS,
    ) -> None:
        timeout_override = os.environ.get("CLAWS_TEMPLE_TASK3_RUNNER_TIMEOUT_SECONDS")
        self.overall_timeout_seconds = (
            overall_timeout_seconds
            if overall_timeout_seconds is not None
            else float(timeout_override or DEFAULT_RUNNER_TIMEOUT_SECONDS)
        )
        self.post_json_grace_seconds = post_json_grace_seconds

    def run_json(self, command: Sequence[str]) -> dict[str, Any]:
        process = subprocess.Popen(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert process.stdout is not None and process.stderr is not None
        stdout_buffer = bytearray()
        stderr_buffer = bytearray()
        parsed_stdout: dict[str, Any] | None = None
        last_valid_stdout: dict[str, Any] | None = None
        last_stdout_at: float | None = None
        deadline = time.monotonic() + max(self.overall_timeout_seconds, 0.1)

        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ, data="stdout")
            selector.register(process.stderr, selectors.EVENT_READ, data="stderr")

            while True:
                now = time.monotonic()
                if (
                    last_valid_stdout is not None
                    and process.poll() is None
                    and last_stdout_at is not None
                    and now - last_stdout_at >= self.post_json_grace_seconds
                ):
                    self._terminate_process(process)
                    return last_valid_stdout

                if process.poll() is not None and not selector.get_map():
                    break

                remaining = deadline - now
                if remaining <= 0:
                    if last_valid_stdout is not None:
                        self._terminate_process(process)
                        return last_valid_stdout
                    self._terminate_process(process)
                    stdout_text = self._decode_buffer(stdout_buffer)
                    stderr_text = self._append_timeout_hint(
                        self._decode_buffer(stderr_buffer),
                        self.overall_timeout_seconds,
                    )
                    raise CommandExecutionError(command, -1, stdout_text, stderr_text)

                events = selector.select(timeout=min(remaining, self.post_json_grace_seconds))
                if not events:
                    if process.poll() is not None:
                        break
                    continue

                for key, _ in events:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    if key.data == "stdout":
                        stdout_buffer.extend(chunk)
                        last_stdout_at = time.monotonic()
                        parsed_stdout = self._try_parse_json(stdout_buffer)
                        if parsed_stdout is not None:
                            last_valid_stdout = parsed_stdout
                    else:
                        stderr_buffer.extend(chunk)

        self._drain_process_output(process, stdout_buffer, stderr_buffer)
        stdout_text = self._decode_buffer(stdout_buffer)
        stderr_text = self._decode_buffer(stderr_buffer)
        if process.returncode != 0:
            raise CommandExecutionError(command, process.returncode, stdout_text, stderr_text)
        if last_valid_stdout is not None:
            return last_valid_stdout
        try:
            return json.loads(stdout_text)
        except json.JSONDecodeError as exc:
            raise CommandExecutionError(command, process.returncode or 0, stdout_text, stderr_text) from exc

    @staticmethod
    def _try_parse_json(buffer: bytearray) -> dict[str, Any] | None:
        text = JsonRunner._decode_buffer(buffer)
        stripped = text.lstrip()
        if not stripped:
            return None
        try:
            payload, _ = json.JSONDecoder().raw_decode(stripped)
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    @staticmethod
    def _decode_buffer(buffer: bytearray) -> str:
        return bytes(buffer).decode("utf-8", errors="replace")

    @staticmethod
    def _append_timeout_hint(stderr_text: str, timeout_seconds: float) -> str:
        timeout_hint = f"command timed out after {timeout_seconds:.1f}s"
        return f"{stderr_text}\n{timeout_hint}".strip()

    @staticmethod
    def _terminate_process(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()

    @staticmethod
    def _drain_process_output(
        process: subprocess.Popen[bytes],
        stdout_buffer: bytearray,
        stderr_buffer: bytearray,
    ) -> None:
        try:
            extra_stdout, extra_stderr = process.communicate(timeout=0.1)
        except subprocess.TimeoutExpired:
            JsonRunner._terminate_process(process)
            extra_stdout, extra_stderr = process.communicate()
        if extra_stdout:
            stdout_buffer.extend(extra_stdout)
        if extra_stderr:
            stderr_buffer.extend(extra_stderr)


@dataclass(slots=True)
class RuntimePaths:
    skill_root: Path
    codex_home: Path
    wallet_context_path: Path

    @classmethod
    def discover(cls, skill_root: Path | None = None) -> "RuntimePaths":
        resolved_skill_root = skill_root or Path(__file__).resolve().parents[1]
        codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
        wallet_context_override = os.environ.get("PORTKEY_SKILL_WALLET_CONTEXT_PATH")
        wallet_context_path = Path(wallet_context_override) if wallet_context_override else Path.home() / ".portkey" / "skill-wallet" / "context.v1.json"
        return cls(
            skill_root=resolved_skill_root,
            codex_home=codex_home,
            wallet_context_path=wallet_context_path,
        )

    @property
    def config_path(self) -> Path:
        return self.skill_root / "config" / "faction-proposals.json"

    @property
    def tomorrowdao_root(self) -> Path:
        return self.codex_home / "skills" / "tomorrowdao-agent-skills"

    @property
    def portkey_root(self) -> Path:
        return self.codex_home / "skills" / "portkey-ca-agent-skills"

    @property
    def portkey_keystore_root(self) -> Path:
        return Path.home() / ".portkey" / "ca"


@dataclass(slots=True)
class WalletProfile:
    login_email: str | None
    keystore_file: Path
    ca_hash: str
    ca_address: str
    manager_address: str | None


@dataclass(slots=True)
class ExecutorState:
    faction: dict[str, Any]
    trace: list[dict[str, Any]] = field(default_factory=list)
    wallet: dict[str, Any] = field(default_factory=dict)
    preflight: dict[str, Any] = field(default_factory=dict)
    transactions: dict[str, Any] = field(default_factory=dict)


class Task3OathExecutor:
    def __init__(
        self,
        args: argparse.Namespace,
        *,
        paths: RuntimePaths | None = None,
        runner: JsonRunner | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self.args = args
        self.paths = paths or RuntimePaths.discover()
        self.runner = runner or JsonRunner()
        self.sleep_fn = sleep_fn or time.sleep
        self.config = self._load_json(self.paths.config_path)
        self.faction = self._resolve_faction(args.faction)
        self.state = ExecutorState(faction=self._faction_public_info(self.faction))
        backoff_override = os.environ.get("CLAWS_TEMPLE_TASK3_RETRY_BACKOFFS")
        if backoff_override:
            self.retry_backoffs = tuple(int(item.strip()) for item in backoff_override.split(",") if item.strip())
        else:
            self.retry_backoffs = DEFAULT_RETRY_BACKOFFS

    def execute(self) -> dict[str, Any]:
        try:
            dependency_info = self._verify_dependencies()
            self.state.preflight["dependencies"] = dependency_info

            self._assert_proposal_is_open()
            self._record("proposal_preflight", "success", {
                "proposalId": self.faction["proposal_id"],
                "endsAt": self.faction["ends_at"],
            })

            wallet = self._resolve_wallet_profile()
            self.state.wallet.update({
                "loginEmail": wallet.login_email,
                "keystoreFile": str(wallet.keystore_file),
                "caHash": wallet.ca_hash,
                "caAddress": wallet.ca_address,
                "managerAddress": wallet.manager_address,
            })

            if not wallet.manager_address:
                if not self._password_value:
                    self._raise_result(
                        status=STATUS_PASSWORD_REQUIRED,
                        stage="wallet",
                        summary="CA keystore password is required to resolve the active manager address.",
                        next_action="ask_for_ca_keystore_password",
                    )
                unlock_data = self._unlock_wallet(wallet)
                wallet = WalletProfile(
                    login_email=unlock_data.get("loginEmail") or wallet.login_email,
                    keystore_file=wallet.keystore_file,
                    ca_hash=unlock_data["caHash"],
                    ca_address=unlock_data["caAddress"],
                    manager_address=unlock_data["managerAddress"],
                )
                self.state.wallet["managerAddress"] = wallet.manager_address

            manager_sync = self._portkey_query(
                "manager-sync-status",
                {
                    "--ca-hash": wallet.ca_hash,
                    "--chain-id": self._chain_id,
                    "--manager-address": wallet.manager_address,
                },
                label="manager sync status",
            )
            self.state.preflight["managerSync"] = manager_sync
            self._record("manager_sync", "success", manager_sync)
            if not manager_sync.get("isManagerSynced"):
                self._raise_result(
                    status=STATUS_BLOCKED,
                    stage="preflight",
                    code="MANAGER_NOT_SYNCED",
                    summary=f"Manager {wallet.manager_address} is not yet synced on {self._chain_id}.",
                    next_action="wait_for_manager_sync",
                )

            vote_payload = self._tomorrowdao(
                "dao",
                "vote",
                {
                    "chainId": self._chain_id,
                    "args": {
                        self.config["dependency_invocation"]["vote_payload"]["proposal_id_field"]: self.faction["proposal_id"],
                        self.config["dependency_invocation"]["vote_payload"]["vote_option_field"]: self.config["dependency_invocation"]["vote_payload"]["vote_option_value"],
                        self.config["dependency_invocation"]["vote_payload"]["vote_amount_field"]: self.config["dependency_invocation"]["vote_payload"]["vote_amount_minimal_unit"],
                    },
                },
                mode="simulate",
                label="vote simulate",
            )
            self.state.preflight["votePayload"] = vote_payload
            self._record("vote_simulate", "success", vote_payload)

            spender_address = vote_payload["contractAddress"]
            balance_data = self._tomorrowdao(
                "token",
                "balance-view",
                {
                    "chainId": self._chain_id,
                    "symbol": self.config["vote_token_symbol"],
                    "owner": wallet.ca_address,
                },
                label="token balance view",
            )
            current_balance = self._extract_numeric(balance_data, keys=("balance", "amount", "value"))
            self.state.preflight["balance"] = {
                "raw": balance_data,
                "amount": current_balance,
                "required": self._vote_amount,
            }
            self._record("balance_check", "success", self.state.preflight["balance"])
            if current_balance < self._vote_amount:
                self._raise_result(
                    status=STATUS_WAITING_FOR_TOKENS,
                    stage="waiting for tokens",
                    summary="AIBOUNTY balance is below the formal Task 3 threshold.",
                    next_action="return_after_task2_or_invite_more_pairs",
                )

            allowance = self._read_allowance(wallet.ca_address, spender_address)
            self.state.preflight["allowance"] = {
                "amount": allowance,
                "required": self._vote_amount,
                "spender": spender_address,
            }
            self._record("allowance_check", "success", self.state.preflight["allowance"])

            password_stage = "ready_to_oath" if allowance >= self._vote_amount else "authorization"
            if not self._password_value:
                self._raise_result(
                    status=STATUS_PASSWORD_REQUIRED,
                    stage=password_stage,
                    summary="CA keystore password is required before the oath write can continue.",
                    next_action="ask_for_ca_keystore_password",
                )

            if allowance < self._vote_amount:
                approve_payload = self._tomorrowdao(
                    "token",
                    "approve",
                    {
                        "chainId": self._chain_id,
                        "args": {
                            self.config["dependency_invocation"]["approve_payload"]["spender_field"]: spender_address,
                            self.config["dependency_invocation"]["approve_payload"]["symbol_field"]: self.config["vote_token_symbol"],
                            self.config["dependency_invocation"]["approve_payload"]["amount_field"]: self._vote_amount,
                        },
                    },
                    mode="simulate",
                    label="approve simulate",
                )
                self.state.preflight["approvePayload"] = approve_payload
                self._record("approve_simulate", "success", approve_payload)
                approve_result = self._retry_forward_call(
                    wallet,
                    phase="approve",
                    payload=approve_payload,
                    reconcile=lambda: self._read_allowance(wallet.ca_address, spender_address),
                    success_predicate=lambda current: current >= self._vote_amount,
                    auxiliary=lambda tx_id: self._poll_transaction(tx_id),
                )
                self.state.transactions["approve"] = approve_result
                self._record("approve_send", "success", approve_result)

            vote_result = self._retry_forward_call(
                wallet,
                phase="vote",
                payload=vote_payload,
                reconcile=lambda: self._vote_reconciliation(wallet, tx_id=None),
                success_predicate=lambda current: current.get("confirmed") is True,
                auxiliary=self._vote_auxiliary_reconciliation(wallet),
            )
            self.state.transactions["vote"] = vote_result
            self._record("vote_send", "success", vote_result)

            vote_tx_id = vote_result.get("transactionId")
            if not vote_tx_id:
                self._raise_result(
                    status=STATUS_SUBMITTED,
                    stage="submitted",
                    code="VOTE_CONFIRMED_WITHOUT_TXID",
                    summary="Vote confirmation was observed, but the final transaction id could not be correlated yet.",
                    next_action="continue_confirmation_polling",
                )
            telegram_payload = self._success_telegram_payload(vote_tx_id)
            return {
                "success": True,
                "status": STATUS_COMPLETED,
                "stage": "completed",
                "summary": "Faction oath completed through the bundled Task 3 executor.",
                "faction": self.state.faction,
                "wallet": self.state.wallet,
                "preflight": self.state.preflight,
                "transactions": self.state.transactions,
                "telegram": telegram_payload,
                "trace": self.state.trace,
            }
        except EarlyResult as result:
            return result.payload
        except Exception as exc:  # pragma: no cover - defensive final boundary
            self._record("unexpected_error", "failure", {"message": str(exc)})
            return {
                "success": False,
                "status": STATUS_BLOCKED,
                "stage": "executor",
                "code": type(exc).__name__,
                "summary": str(exc),
                "faction": self.state.faction,
                "wallet": self.state.wallet,
                "preflight": self.state.preflight,
                "transactions": self.state.transactions,
                "trace": self.state.trace,
            }

    @property
    def _chain_id(self) -> str:
        return str(self.config["dependency_invocation"]["network_id"])

    @property
    def _vote_amount(self) -> int:
        return int(self.config["vote_amount_minimal_unit"])

    @property
    def _password_value(self) -> str | None:
        return self.args.password or os.environ.get("PORTKEY_CA_KEYSTORE_PASSWORD")

    def _load_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _verify_dependencies(self) -> dict[str, Any]:
        tomorrowdao_root = self.paths.tomorrowdao_root
        portkey_root = self.paths.portkey_root
        checks = {
            "tomorrowdao-agent-skills": {
                "root": str(tomorrowdao_root),
                "package": tomorrowdao_root / "package.json",
                "minVersion": self.config["dependency_min_version"],
            },
            "portkey-ca-agent-skills": {
                "root": str(portkey_root),
                "package": portkey_root / "package.json",
                "minVersion": self.config["ca_write_dependency_min_version"],
            },
        }
        resolved: dict[str, Any] = {}
        for name, meta in checks.items():
            package_path = Path(meta["package"])
            if not package_path.exists():
                self._raise_result(
                    status=STATUS_BLOCKED,
                    stage="dependency",
                    code="DEPENDENCY_MISSING",
                    summary=f"{name} is missing from {package_path.parent}.",
                    next_action="run_dependency_self_heal",
                )
            version = self._load_json(package_path).get("version")
            if not version or not self._version_gte(str(version), str(meta["minVersion"])):
                self._raise_result(
                    status=STATUS_BLOCKED,
                    stage="dependency",
                    code="DEPENDENCY_VERSION_TOO_LOW",
                    summary=f"{name} version {version or 'unknown'} is below required {meta['minVersion']}.",
                    next_action="run_dependency_self_heal",
                )
            resolved[name] = {
                "root": meta["root"],
                "version": version,
                "minVersion": meta["minVersion"],
            }
        self._record("dependency_check", "success", resolved)
        return resolved

    def _resolve_wallet_profile(self) -> WalletProfile:
        active_profile = self._read_active_wallet_profile()
        keystore_path = self._resolve_keystore_path(active_profile)
        if not keystore_path.exists():
            self._raise_result(
                status=STATUS_BLOCKED,
                stage="wallet",
                code="KEYSTORE_NOT_FOUND",
                summary=f"Task 3 could not find a CA keystore at {keystore_path}.",
                next_action="recover_and_save_or_select_correct_profile",
            )
        keystore_payload = self._load_json(keystore_path)
        ca_hash = str(keystore_payload.get("caHash") or "")
        ca_address = str(keystore_payload.get("caAddress") or "")
        login_email = self.args.login_email or keystore_payload.get("loginEmail") or active_profile.get("loginEmail") or None
        manager_address = None
        active_keystore = active_profile.get("keystoreFile")
        if active_profile and active_keystore and Path(str(active_keystore)).expanduser().resolve() == keystore_path:
            manager_address = active_profile.get("address")
        profile = WalletProfile(
            login_email=str(login_email) if login_email else None,
            keystore_file=keystore_path,
            ca_hash=ca_hash,
            ca_address=ca_address,
            manager_address=str(manager_address) if manager_address else None,
        )
        if not profile.ca_hash or not profile.ca_address:
            self._raise_result(
                status=STATUS_BLOCKED,
                stage="wallet",
                code="KEYSTORE_METADATA_INVALID",
                summary="Task 3 could not resolve CA metadata from the selected keystore.",
                next_action="recover_and_save_or_select_correct_profile",
            )
        self._record("wallet_profile", "success", {
            "loginEmail": profile.login_email,
            "keystoreFile": str(profile.keystore_file),
            "caHash": profile.ca_hash,
            "caAddress": profile.ca_address,
            "managerAddress": profile.manager_address,
        })
        return profile

    def _unlock_wallet(self, wallet: WalletProfile) -> dict[str, Any]:
        try:
            unlock_data = self._portkey_auth(
                "unlock",
                {
                    "--password": self._password_value,
                    "--login-email": wallet.login_email,
                    "--keystore-file": str(wallet.keystore_file),
                },
                label="wallet unlock",
            )
        except (CommandExecutionError, ToolResponseError) as exc:
            if self._is_password_error(exc):
                self._raise_password_required(stage="wallet")
            raise
        self._record("wallet_unlock", "success", unlock_data)
        return unlock_data

    def _read_allowance(self, owner: str, spender: str) -> int:
        allowance_data = self._tomorrowdao(
            "token",
            "allowance-view",
            {
                "chainId": self._chain_id,
                "symbol": self.config["vote_token_symbol"],
                "owner": owner,
                "spender": spender,
            },
            label="token allowance view",
        )
        return self._extract_numeric(allowance_data, keys=("allowance", "amount", "value"))

    def _retry_forward_call(
        self,
        wallet: WalletProfile,
        *,
        phase: str,
        payload: dict[str, Any],
        reconcile: Callable[[], Any],
        success_predicate: Callable[[Any], bool],
        auxiliary: Callable[[str | None], Any] | None,
    ) -> dict[str, Any]:
        last_error: str | None = None
        last_tx_result: dict[str, Any] | None = None
        for attempt, delay in enumerate(self.retry_backoffs, start=1):
            try:
                result = self._portkey_tx(
                    "forward-call",
                    {
                        "--ca-hash": wallet.ca_hash,
                        "--contract-address": payload["contractAddress"],
                        "--method-name": payload["methodName"],
                        "--args": json.dumps(payload["args"], separators=(",", ":")),
                        "--chain-id": self._chain_id,
                        "--login-email": wallet.login_email,
                        "--keystore-file": str(wallet.keystore_file),
                        "--password": self._password_value,
                    },
                    label=f"{phase} forward call",
                )
                tx_result = self._normalize_portkey_tx_result(result)
                last_tx_result = tx_result
                if tx_result["status"] == "MINED":
                    return tx_result
                last_error = tx_result.get("error") or tx_result["status"]
                is_terminal_failure = self._tx_status_is_terminal_failure(tx_result["status"])
                try:
                    reconciled = reconcile()
                except (CommandExecutionError, ToolResponseError):
                    reconciled = None
                if reconciled is not None and success_predicate(reconciled):
                    tx_result["reconciled"] = reconciled
                    tx_result["status"] = "MINED"
                    return tx_result
                if auxiliary:
                    try:
                        extra = auxiliary(tx_result.get("transactionId"))
                    except (CommandExecutionError, ToolResponseError):
                        extra = None
                    if extra is not None and success_predicate(extra):
                        tx_result["reconciled"] = extra
                        tx_result["status"] = "MINED"
                        return tx_result
                if is_terminal_failure:
                    self.state.transactions[phase] = tx_result
                    break
            except (CommandExecutionError, ToolResponseError) as exc:
                if self._is_password_error(exc):
                    self._raise_password_required(stage=self._forward_password_stage(phase))
                last_error = str(exc)
                self._record(f"{phase}_attempt", "failure", {"attempt": attempt, "message": last_error})
                try:
                    reconciled = reconcile()
                except (CommandExecutionError, ToolResponseError):
                    reconciled = None
                if reconciled is not None and success_predicate(reconciled):
                    return {
                        "status": "MINED",
                        "transactionId": None,
                        "error": last_error,
                        "reconciled": reconciled,
                    }
                if auxiliary:
                    try:
                        extra = auxiliary(None)
                    except (CommandExecutionError, ToolResponseError):
                        extra = None
                    if extra is not None and success_predicate(extra):
                        return {
                            "status": "MINED",
                            "transactionId": None,
                            "error": last_error,
                            "reconciled": extra,
                        }
            if attempt < len(self.retry_backoffs):
                self._record(f"{phase}_retry", "pending", {"attempt": attempt, "delaySeconds": delay})
                if not os.environ.get("CLAWS_TEMPLE_TASK3_EXECUTOR_SKIP_SLEEP"):
                    self.sleep_fn(delay)
        if (
            phase == "vote"
            and last_tx_result
            and last_tx_result.get("transactionId")
            and not self._tx_status_is_terminal_failure(last_tx_result.get("status"))
        ):
            self.state.transactions[phase] = last_tx_result
            self._raise_result(
                status=STATUS_SUBMITTED,
                stage="submitted",
                code="VOTE_SUBMITTED_AWAITING_CONFIRMATION",
                summary="Vote transaction was submitted and is still waiting for final confirmation.",
                next_action="continue_confirmation_polling",
            )
        self._raise_result(
            status=STATUS_BLOCKED,
            stage=phase,
            code=f"{phase.upper()}_FAILED",
            summary=f"{phase.capitalize()} could not be confirmed after bounded retries: {last_error or 'unknown error'}",
            next_action="inspect_maintainer_trace_or_support",
        )
        raise AssertionError("unreachable")

    def _poll_transaction(self, tx_id: str | None) -> dict[str, Any]:
        if not tx_id:
            return {"confirmed": False}
        receipt = self._portkey_query(
            "tx-result",
            {
                "--tx-id": tx_id,
                "--chain-id": self._chain_id,
            },
            label="transaction result",
        )
        return {
            "confirmed": receipt.get("Status") == "MINED",
            "receipt": receipt,
        }

    def _vote_auxiliary_reconciliation(self, wallet: WalletProfile) -> Callable[[str | None], dict[str, Any]]:
        def _inner(tx_id: str | None) -> dict[str, Any]:
            receipt_info = self._poll_transaction(tx_id) if tx_id else {"confirmed": False}
            if receipt_info.get("confirmed"):
                return receipt_info
            try:
                proposal_my_info = self._tomorrowdao(
                    "dao",
                    "proposal-my-info",
                    {
                        "chainId": self._chain_id,
                        "proposalId": self.faction["proposal_id"],
                        "address": wallet.ca_address,
                        "daoId": self.config["dao_id"],
                    },
                    label="proposal my-info",
                )
            except (CommandExecutionError, ToolResponseError):
                return {"confirmed": False, "receipt": receipt_info.get("receipt")}
            vote_amount = self._extract_numeric(proposal_my_info, keys=("voteAmount", "amount", "value"), default=0)
            return {
                "confirmed": vote_amount >= self._vote_amount,
                "receipt": receipt_info.get("receipt"),
                "proposalMyInfo": proposal_my_info,
            }

        return _inner

    def _vote_reconciliation(self, wallet: WalletProfile, tx_id: str | None) -> dict[str, Any]:
        auxiliary = self._vote_auxiliary_reconciliation(wallet)
        return auxiliary(tx_id)

    def _normalize_portkey_tx_result(self, data: dict[str, Any]) -> dict[str, Any]:
        inner = data.get("data") or {}
        status = str(inner.get("Status") or data.get("status") or "UNKNOWN").upper()
        return {
            "transactionId": data.get("transactionId") or inner.get("TransactionId"),
            "status": status,
            "error": inner.get("Error"),
            "receipt": inner,
            "feePreview": data.get("feePreview"),
            "caAddress": data.get("caAddress"),
        }

    @staticmethod
    def _is_password_error(error: Exception | str) -> bool:
        message = str(error).lower()
        return any(marker in message for marker in PASSWORD_ERROR_MARKERS)

    @staticmethod
    def _tx_status_is_terminal_failure(status: str | None) -> bool:
        return str(status or "").upper() in TERMINAL_TX_FAILURE_STATUSES

    @staticmethod
    def _forward_password_stage(phase: str) -> str:
        return "authorization" if phase == "approve" else "ready_to_oath"

    def _raise_password_required(self, *, stage: str) -> None:
        self._raise_result(
            status=STATUS_PASSWORD_REQUIRED,
            stage=stage,
            code="PASSWORD_REJECTED",
            summary="The provided CA keystore password was rejected.",
            next_action="ask_for_ca_keystore_password",
        )

    def _tomorrowdao(
        self,
        domain: str,
        command: str,
        input_payload: dict[str, Any],
        *,
        mode: str | None = None,
        label: str,
    ) -> dict[str, Any]:
        cli = [
            "bun",
            "run",
            str(self.paths.tomorrowdao_root / "tomorrowdao_skill.ts"),
            domain,
            command,
            "--input",
            json.dumps(input_payload, separators=(",", ":")),
        ]
        if mode:
            cli.extend(["--mode", mode])
        payload = self.runner.run_json(cli)
        if not payload.get("success"):
            raise ToolResponseError(label, payload)
        return dict(payload.get("data") or {})

    def _portkey_auth(self, command: str, options: dict[str, Any], *, label: str) -> dict[str, Any]:
        return self._portkey_cli("portkey_auth_skill.ts", command, options, label=label)

    def _portkey_query(self, command: str, options: dict[str, Any], *, label: str) -> dict[str, Any]:
        return self._portkey_cli("portkey_query_skill.ts", command, options, label=label)

    def _portkey_tx(self, command: str, options: dict[str, Any], *, label: str) -> dict[str, Any]:
        return self._portkey_cli("portkey_tx_skill.ts", command, options, label=label)

    def _portkey_cli(self, script_name: str, command: str, options: dict[str, Any], *, label: str) -> dict[str, Any]:
        cli = [
            "bun",
            "run",
            str(self.paths.portkey_root / script_name),
            command,
        ]
        for key, value in options.items():
            if value is None or value == "":
                continue
            cli.extend([key, str(value)])
        payload = self.runner.run_json(cli)
        if payload.get("status") != "success":
            raise ToolResponseError(label, payload)
        return dict(payload.get("data") or {})

    def _resolve_keystore_path(self, active_profile: dict[str, Any]) -> Path:
        if self.args.keystore_file:
            return Path(self.args.keystore_file).expanduser().resolve()
        active_keystore = active_profile.get("keystoreFile")
        if active_keystore:
            return Path(str(active_keystore)).expanduser().resolve()
        login_email = self.args.login_email or active_profile.get("loginEmail")
        if login_email:
            return self.paths.portkey_keystore_root / DEFAULT_NETWORK / f"{quote(str(login_email).strip().lower(), safe='')}.keystore.json"
        self._raise_result(
            status=STATUS_BLOCKED,
            stage="wallet",
            code="CA_CONTEXT_NOT_FOUND",
            summary="Task 3 could not resolve an active CA keystore profile.",
            next_action="recover_and_save_or_select_correct_profile",
        )
        raise AssertionError("unreachable")

    def _read_active_wallet_profile(self) -> dict[str, Any]:
        context_path = self.paths.wallet_context_path
        if not context_path.exists():
            return {}
        try:
            context = self._load_json(context_path)
        except Exception:
            return {}
        active_profile_id = context.get("activeProfileId")
        profiles = context.get("profiles") or {}
        if not isinstance(profiles, dict):
            return {}
        candidate = profiles.get(active_profile_id) if active_profile_id else None
        if not isinstance(candidate, dict):
            return {}
        if candidate.get("walletType") != "CA" or candidate.get("source") != "ca-keystore":
            return {}
        return candidate

    def _assert_proposal_is_open(self) -> None:
        ends_at = str(self.faction["ends_at"])
        if self._parse_timestamp(ends_at) <= datetime.now(ZoneInfo("Asia/Shanghai")):
            self._raise_result(
                status=STATUS_BLOCKED,
                stage="preflight",
                code="PROPOSAL_EXPIRED",
                summary=f"Faction proposal {self.faction['proposal_id']} is no longer open.",
                next_action="refresh_faction_mapping",
            )

    def _resolve_faction(self, raw_faction: str) -> dict[str, Any]:
        normalized = self._normalize_alias(raw_faction)
        for faction in self.config["factions"]:
            aliases = {
                self._normalize_alias(faction["brand_key"]),
                self._normalize_alias(faction["internal_proposal_name"]),
                self._normalize_alias(faction["display_name"]["zh-CN"]),
                self._normalize_alias(faction["display_name"]["en"]),
            }
            if normalized in aliases:
                return faction
        available = ", ".join(item["brand_key"] for item in self.config["factions"])
        raise SystemExit(f"Unknown faction '{raw_faction}'. Available: {available}")

    def _faction_public_info(self, faction: dict[str, Any]) -> dict[str, Any]:
        return {
            "brandKey": faction["brand_key"],
            "displayName": faction["display_name"],
            "coreStance": faction["core_stance"],
            "proposalId": faction["proposal_id"],
            "endsAt": faction["ends_at"],
        }

    def _record(self, step: str, status: str, details: dict[str, Any]) -> None:
        self.state.trace.append({
            "step": step,
            "status": status,
            "details": details,
        })

    def _raise_result(
        self,
        *,
        status: str,
        stage: str,
        summary: str,
        next_action: str,
        code: str | None = None,
    ) -> None:
        payload = {
            "success": False,
            "status": status,
            "stage": stage,
            "summary": summary,
            "nextAction": next_action,
            "faction": self.state.faction,
            "wallet": self.state.wallet,
            "preflight": self.state.preflight,
            "transactions": self.state.transactions,
            "trace": self.state.trace,
        }
        if code:
            payload["code"] = code
        raise EarlyResult(payload)

    def _success_telegram_payload(self, tx_id: str | None) -> dict[str, Any]:
        tx_token = tx_id or "pending-tx"
        template = self.config["success_telegram_template"]
        return {
            "groupUrl": self.config["success_telegram_group_url"],
            "bonusNote": self.config["success_bonus_note"],
            "template": {
                locale: value.replace("{faction_name}", self.faction["display_name"][locale]).replace("{txId}", tx_token)
                for locale, value in template.items()
            },
            "txId": tx_id,
        }

    @staticmethod
    def _normalize_alias(value: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "", value or "")
        return cleaned.strip().lower()

    @staticmethod
    def _version_gte(actual: str, minimum: str) -> bool:
        return Task3OathExecutor._parse_version(actual) >= Task3OathExecutor._parse_version(minimum)

    @staticmethod
    def _parse_version(raw: str) -> tuple[int, ...]:
        return tuple(int(part) for part in str(raw).split(".") if part.isdigit())

    @staticmethod
    def _parse_timestamp(raw: str) -> datetime:
        match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) ([A-Za-z_./+-]+)", raw.strip())
        if not match:
            raise ValueError(f"unsupported timestamp format: {raw}")
        date_part, time_part, timezone_name = match.groups()
        return datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(timezone_name))

    @staticmethod
    def _extract_numeric(data: Any, *, keys: Sequence[str], default: int | None = None) -> int:
        if isinstance(data, bool):
            value: Any = int(data)
        elif isinstance(data, (int, float)):
            value = data
        elif isinstance(data, str):
            value = data.strip()
        elif isinstance(data, dict):
            for key in keys:
                if key in data:
                    return Task3OathExecutor._extract_numeric(data[key], keys=keys, default=default)
            for candidate_key in ("amount", "balance", "allowance", "voteAmount", "value"):
                if candidate_key in data:
                    return Task3OathExecutor._extract_numeric(data[candidate_key], keys=keys, default=default)
            if default is not None:
                return default
            raise ValueError(f"could not extract numeric value from {data}")
        else:
            if default is not None:
                return default
            raise ValueError(f"unsupported numeric payload: {data!r}")

        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            if default is not None:
                return default
            raise ValueError(f"could not coerce numeric value from {value!r}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Single-entry Task 3 executor for the Claws Temple faction oath flow.",
    )
    parser.add_argument("--faction", required=True, help="Faction alias: brand key, zh name, or en name.")
    parser.add_argument("--login-email", help="Optional Portkey login email for the CA keystore profile.")
    parser.add_argument("--keystore-file", help="Optional explicit CA keystore file path.")
    parser.add_argument("--password", help="Optional CA keystore password. Falls back to PORTKEY_CA_KEYSTORE_PASSWORD.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    executor = Task3OathExecutor(args)
    payload = executor.execute()
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if payload.get("status") in NON_BLOCKING_EXIT_STATUSES else 1


if __name__ == "__main__":
    raise SystemExit(main())
