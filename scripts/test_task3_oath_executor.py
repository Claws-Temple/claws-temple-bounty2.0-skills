#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "claws-temple-bounty" / "scripts" / "task3-oath-executor.py"
SPEC = importlib.util.spec_from_file_location("task3_oath_executor", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FakeRunner(MODULE.JsonRunner):
    def __init__(self, responses: dict[tuple[str, ...], list[object]]) -> None:
        self.responses = {key: list(value) for key, value in responses.items()}
        self.commands: list[list[str]] = []

    def run_json(self, command):
        command = list(command)
        self.commands.append(command)
        key = self._key_for(command)
        queue = self.responses.get(key)
        if not queue:
            raise AssertionError(f"unexpected command: {command}")
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    @staticmethod
    def _key_for(command: list[str]) -> tuple[str, ...]:
        script = Path(command[2]).name
        if script == "tomorrowdao_skill.ts":
            return (script, command[3], command[4])
        return (script, command[3])


class Task3ExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.codex_home = self.base / ".codex"
        self.wallet_context = self.base / "context.v1.json"
        self.keystore_file = self.base / "demo.keystore.json"
        self.keystore_file.write_text(
            json.dumps(
                {
                    "caHash": "ca-demo",
                    "caAddress": "ELF_demo_tDVV",
                    "loginEmail": "demo@example.com",
                    "originChainId": "AELF",
                    "keystore": {},
                }
            ),
            encoding="utf-8",
        )
        for skill_name, version in (
            ("tomorrowdao-agent-skills", "0.2.2"),
            ("portkey-ca-agent-skills", "2.3.0"),
        ):
            package_dir = self.codex_home / "skills" / skill_name
            package_dir.mkdir(parents=True, exist_ok=True)
            (package_dir / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
        self.paths = MODULE.RuntimePaths(
            skill_root=ROOT / "skills" / "claws-temple-bounty",
            codex_home=self.codex_home,
            wallet_context_path=self.wallet_context,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_active_wallet(self, *, manager_address: str | None = "ELF_manager_tDVV") -> None:
        self.wallet_context.write_text(
            json.dumps(
                {
                    "version": 1,
                    "activeProfileId": "default",
                    "profiles": {
                        "default": {
                            "walletType": "CA",
                            "source": "ca-keystore",
                            "network": "mainnet",
                            "address": manager_address,
                            "loginEmail": "demo@example.com",
                            "caAddress": "ELF_demo_tDVV",
                            "caHash": "ca-demo",
                            "keystoreFile": str(self.keystore_file),
                            "updatedAt": "2026-04-02T00:00:00+08:00",
                        }
                    },
                    "lastWriter": {"skill": "portkey-ca", "version": "2.3.0"},
                }
            ),
            encoding="utf-8",
        )

    def _executor(self, runner: FakeRunner, *, password: str | None = None) -> MODULE.Task3OathExecutor:
        args = Namespace(
            faction="记录者",
            login_email=None,
            keystore_file=None,
            password=password,
        )
        return MODULE.Task3OathExecutor(args, paths=self.paths, runner=runner, sleep_fn=lambda _: None)

    def test_returns_waiting_for_tokens_before_password(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "1"}}
                ],
            }
        )

        result = self._executor(runner).execute()

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "waiting_for_tokens")
        self.assertEqual(result["stage"], "waiting for tokens")

    def test_returns_password_required_after_preflight(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "200000000"}}
                ],
                ("tomorrowdao_skill.ts", "token", "allowance-view"): [
                    {"success": True, "data": {"allowance": "200000000"}}
                ],
            }
        )

        result = self._executor(runner).execute()

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "password_required")
        self.assertEqual(result["stage"], "ready_to_oath")

    def test_completes_oath_with_approve_and_vote(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "200000000"}}
                ],
                ("tomorrowdao_skill.ts", "token", "allowance-view"): [
                    {"success": True, "data": {"allowance": "0"}},
                    {"success": True, "data": {"allowance": "200000000"}},
                ],
                ("tomorrowdao_skill.ts", "token", "approve"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "token-contract",
                            "methodName": "Approve",
                            "args": {"spender": "vote-contract", "symbol": "AIBOUNTY", "amount": 200000000},
                        },
                    }
                ],
                ("portkey_tx_skill.ts", "forward-call"): [
                    {
                        "status": "success",
                        "data": {
                            "transactionId": "approve-tx",
                            "data": {"TransactionId": "approve-tx", "Status": "MINED", "Error": None},
                            "caAddress": "ELF_demo_tDVV",
                        },
                    },
                    {
                        "status": "success",
                        "data": {
                            "transactionId": "vote-tx",
                            "data": {"TransactionId": "vote-tx", "Status": "MINED", "Error": None},
                            "caAddress": "ELF_demo_tDVV",
                        },
                    },
                ],
            }
        )

        result = self._executor(runner, password="secret").execute()

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["transactions"]["approve"]["transactionId"], "approve-tx")
        self.assertEqual(result["transactions"]["vote"]["transactionId"], "vote-tx")
        self.assertEqual(result["telegram"]["txId"], "vote-tx")

    def test_returns_submitted_when_vote_confirmation_is_still_pending(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "200000000"}}
                ],
                ("tomorrowdao_skill.ts", "token", "allowance-view"): [
                    {"success": True, "data": {"allowance": "200000000"}}
                ],
                ("portkey_tx_skill.ts", "forward-call"): [
                    {
                        "status": "success",
                        "data": {
                            "transactionId": "vote-tx",
                            "data": {"TransactionId": "vote-tx", "Status": "PENDING", "Error": None},
                            "caAddress": "ELF_demo_tDVV",
                        },
                    }
                ],
                ("portkey_query_skill.ts", "tx-result"): [
                    {"status": "success", "data": {"TransactionId": "vote-tx", "Status": "PENDING", "Error": None}}
                ],
                ("tomorrowdao_skill.ts", "dao", "proposal-my-info"): [
                    {"success": True, "data": {"voteAmount": "0"}},
                    {"success": True, "data": {"voteAmount": "0"}},
                ],
            }
        )

        executor = self._executor(runner, password="secret")
        executor.retry_backoffs = (0,)

        result = executor.execute()

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "submitted")
        self.assertEqual(result["transactions"]["vote"]["transactionId"], "vote-tx")

    def test_blocks_when_vote_write_returns_terminal_failure(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "200000000"}}
                ],
                ("tomorrowdao_skill.ts", "token", "allowance-view"): [
                    {"success": True, "data": {"allowance": "200000000"}}
                ],
                ("portkey_tx_skill.ts", "forward-call"): [
                    {
                        "status": "success",
                        "data": {
                            "transactionId": "vote-tx",
                            "data": {"TransactionId": "vote-tx", "Status": "FAILED", "Error": "insufficient"},
                            "caAddress": "ELF_demo_tDVV",
                        },
                    }
                ],
                ("portkey_query_skill.ts", "tx-result"): [
                    {"status": "success", "data": {"TransactionId": "vote-tx", "Status": "FAILED", "Error": "insufficient"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "proposal-my-info"): [
                    {"success": True, "data": {"voteAmount": "0"}},
                    {"success": True, "data": {"voteAmount": "0"}},
                ],
            }
        )

        executor = self._executor(runner, password="secret")
        executor.retry_backoffs = (0,)
        result = executor.execute()

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["stage"], "vote")
        self.assertEqual(result["code"], "VOTE_FAILED")

    def test_returns_password_required_when_forward_call_rejects_password(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "200000000"}}
                ],
                ("tomorrowdao_skill.ts", "token", "allowance-view"): [
                    {"success": True, "data": {"allowance": "200000000"}}
                ],
                ("portkey_tx_skill.ts", "forward-call"): [
                    MODULE.CommandExecutionError(
                        ["bun", "run", "portkey_tx_skill.ts", "forward-call"],
                        1,
                        "",
                        "Failed to decrypt keystore. The password may be incorrect.",
                    )
                ],
            }
        )

        result = self._executor(runner, password="wrong-password").execute()

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "password_required")
        self.assertEqual(result["stage"], "ready_to_oath")
        self.assertEqual(result["code"], "PASSWORD_REJECTED")

    def test_returns_submitted_when_vote_is_confirmed_without_correlated_txid(self) -> None:
        self._write_active_wallet(manager_address="ELF_manager_tDVV")
        runner = FakeRunner(
            {
                ("portkey_query_skill.ts", "manager-sync-status"): [
                    {"status": "success", "data": {"isManagerSynced": True, "caAddress": "ELF_demo_tDVV"}}
                ],
                ("tomorrowdao_skill.ts", "dao", "vote"): [
                    {
                        "success": True,
                        "data": {
                            "contractAddress": "vote-contract",
                            "methodName": "Vote",
                            "args": {"votingItemId": "proposal-1", "voteOption": 0, "voteAmount": 200000000},
                        },
                    }
                ],
                ("tomorrowdao_skill.ts", "token", "balance-view"): [
                    {"success": True, "data": {"balance": "200000000"}}
                ],
                ("tomorrowdao_skill.ts", "token", "allowance-view"): [
                    {"success": True, "data": {"allowance": "200000000"}}
                ],
                ("portkey_tx_skill.ts", "forward-call"): [
                    MODULE.CommandExecutionError(
                        ["bun", "run", "portkey_tx_skill.ts", "forward-call"],
                        1,
                        "",
                        "transport timeout",
                    )
                ],
                ("tomorrowdao_skill.ts", "dao", "proposal-my-info"): [
                    {"success": True, "data": {"voteAmount": "200000000"}}
                ],
            }
        )

        executor = self._executor(runner, password="secret")
        executor.retry_backoffs = (0,)
        result = executor.execute()

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "submitted")
        self.assertEqual(result["code"], "VOTE_CONFIRMED_WITHOUT_TXID")
        self.assertIsNone(result["transactions"]["vote"]["transactionId"])

    def test_main_returns_zero_for_recoverable_statuses(self) -> None:
        class StubExecutor:
            def __init__(self, _args) -> None:
                pass

            def execute(self) -> dict[str, object]:
                return {"success": False, "status": "password_required"}

        with mock.patch.object(MODULE, "Task3OathExecutor", StubExecutor):
            with redirect_stdout(io.StringIO()):
                code = MODULE.main(["--faction", "记录者"])

        self.assertEqual(code, 0)

    def test_main_returns_one_for_blocked_status(self) -> None:
        class StubExecutor:
            def __init__(self, _args) -> None:
                pass

            def execute(self) -> dict[str, object]:
                return {"success": False, "status": "blocked"}

        with mock.patch.object(MODULE, "Task3OathExecutor", StubExecutor):
            with redirect_stdout(io.StringIO()):
                code = MODULE.main(["--faction", "记录者"])

        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
