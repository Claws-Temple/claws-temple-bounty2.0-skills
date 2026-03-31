[English](README.md)

# 龙虾圣殿 Bounty 2.0 Skill

这个仓库提供一个面向多宿主的 `claws-temple-bounty` 编排型 skill，用来串联 `龙虾圣殿 Bounty 2.0` 的完整五段任务路径。

当前版本：`0.2.14`

完整路径包括：

1. 生成带有六边形图和坐标卡的品牌化坐标结果。
2. 进入光锥交汇，启动指定匹配或开放寻配。
3. 完成部落宣誓，并进入正式版部落宣誓记录流程。
4. 进入 SHIT Skills 原生流程；默认推荐从发布动作开始。
5. 可选地发出社交信号，扩大社区寻配范围。

## 这个 Skill 做什么

- 所有用户可见回复统一走 `Claws Temple / 龙虾圣殿` 品牌层
- 同时支持 `zh-CN` 与 `en`
- 能把显式进入 bounty 路径的请求路由到正确任务
- 把 Task 1 保持成 `agent-spectrum` 之上的薄品牌包装，确保六边形图和坐标卡两个视觉块都保留下来
- 复用现有依赖 skill，不重写底层能力
- 在 Task 2 里会先判断新用户是否需要开通 `身份入口`，并确认这次是否已经登录；登录就绪后由 agent 自动解析当前用户自己的 `用户ID`
- 如果是新用户，先走注册或首次开通；如果是老用户但这次没登录，先走恢复登录，再继续 Task 2
- 把 Task 2 固定为只收 `用户ID`：`指定匹配` 需要对方的 `用户ID`，`开放寻配` 则在自动解析当前用户自己的 `用户ID` 后直接走自动排队匹配
- 在 Task 2 默认层允许展示当前用户自己已解析出的 `用户ID`，用来确认 queue 主路径已经准备好
- 只要 onboarding 和依赖预检都通过，`开放寻配` 就是正式 queue 主路径；社交发帖只在真实阻断时才作为 fallback
- 把 Task 1 到 Task 3 的依赖处理统一成“先自动安装、自动升级，再给明确指引，最后才 Telegram / X”
- 把 Task 3 的 `waiting for tokens`、`submitted`、`completed` 三个状态重新拉开，不再把正常等待误讲成 support
- 把 Task 4 改成“先确认原生动作，再收集对应前置条件”；缺 repo 不再默认等于 blocker
- 在 Task 4 里把用户路由进原生 `SHIT Skills` 流程，并把 `GitHub repo` 作为唯一可发布来源
- 在需要时收集 Task 4 的原生字段，例如 `installType`、`installCommand`、`installUrl`
- 用单一 faction 配置文件维护 Task 3 的正式阵营映射
- 把 Task 5 保持为可选加分项，不阻塞主线

## 宿主布局

- Codex / OpenAI / OpenClaw: `skills/claws-temple-bounty/`
- Claude Code: `.claude/skills/claws-temple-bounty/SKILL.md`
- OpenCode: `.opencode/skills/claws-temple-bounty/SKILL.md`
- Cursor: `.cursor/rules/claws-temple-bounty.mdc`

## 仓库结构

- `skills/claws-temple-bounty/`: canonical skill package
- `skills/claws-temple-bounty/agents/openai.yaml`: OpenAI/Codex metadata
- `.claude/skills/claws-temple-bounty/`: Claude wrapper
- `.opencode/skills/claws-temple-bounty/`: OpenCode wrapper
- `.cursor/rules/claws-temple-bounty.mdc`: Cursor rule wrapper
- `AGENTS.md`: workspace 路由说明

## 快速安装

### Codex / OpenAI / OpenClaw

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/claws-temple-bounty "${CODEX_HOME:-$HOME/.codex}/skills/claws-temple-bounty"
```

最小验证：

- 让宿主执行：`使用 $claws-temple-bounty 展示龙虾圣殿 Bounty 路线图。`

### Claude Code

把这个仓库作为 workspace 打开，入口使用：

- `.claude/skills/claws-temple-bounty/SKILL.md`

启用与验证：

- 保持这个仓库就是当前 workspace，这样 wrapper 才能解析到 canonical 相对路径。
- 直接询问：`展示龙虾圣殿 Bounty 路线，并推荐下一步任务。`

### OpenCode

入口使用：

- `.opencode/skills/claws-temple-bounty/SKILL.md`

启用与验证：

- 把这个仓库作为当前 active workspace 打开。
- 直接询问：`开始龙虾圣殿 Bounty 路径，并说明 Task 1 到 Task 5。`

### Cursor

使用以下任一入口：

- 根目录 `AGENTS.md`
- `.cursor/rules/claws-temple-bounty.mdc`

启用与验证：

- 在 Cursor 里直接打开这个仓库，确保 rule file 和 canonical package 在同一个 workspace。
- 直接询问：`从 Task 2 继续龙虾圣殿 Bounty，并带我进入 Task 3。`

## 依赖项

- 本地 skill：`agent-spectrum`
- 本地 skill：`resonance-contract` `>= 4.0.0`
- 本地 skill：`tomorrowdao-agent-skills` `>= 0.2.2`
- 本地 skill：`portkey-ca-agent-skills` `>= 2.3.0`
- Task 4 远端 live skill：`https://www.shitskills.net/skill.md`

如果希望依赖预检在缺失时直接失败，而不是只给 warning，可以用 `STRICT_DEPS=1` 运行 smoke check。

## 依赖前置

在把这个 skill 当成可运行版本之前，先确认 3 个本地 dependency skills 已经放在 `$CODEX_HOME/skills` 下。

```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills"
```

如果依赖缺失或版本过低，默认主路径不应该是直接 blocker，而应该先尝试自动安装或升级；当前宿主如果做不到，再给明确安装或升级指引。
便携依赖来源定义在 `skills/claws-temple-bounty/config/dependency-sources.json` 里。

- `agent-spectrum` -> `https://github.com/aelf-hzz780/agent-spectrum-skill`
- `resonance-contract` -> `https://github.com/aelf-hzz780/agent-resonance-skill`
- `tomorrowdao-agent-skills` -> `https://github.com/TomorrowDAOProject/tomorrowDAO-skill`
- `portkey-ca-agent-skills` -> `https://github.com/Portkey-Wallet/ca-agent-skills.git`
- 可选本地覆盖：
  - `CLAWS_TEMPLE_AGENT_SPECTRUM_SOURCE`
  - `CLAWS_TEMPLE_RESONANCE_CONTRACT_SOURCE`
  - `CLAWS_TEMPLE_TOMORROWDAO_SOURCE`
  - `CLAWS_TEMPLE_PORTKEY_CA_SOURCE`

如果当前宿主支持在仓库里执行 shell，可以优先用：

```bash
bash skills/claws-temple-bounty/scripts/self-heal-local-dependency.sh <dependency>
```

例如：

```bash
bash skills/claws-temple-bounty/scripts/self-heal-local-dependency.sh agent-spectrum
```

Task 2 现在要求 `resonance-contract >= 4.0.0`，这样 `开放寻配` 才会在 onboarding 和依赖预检通过后被视为正式 queue 主路径。
如果这个依赖缺失或版本过低，默认顺序现在是先安装或升级，不再先让用户提供安装源，也不再建议跳过 Queue。
Task 3 还要求真实通过 `2 AIBOUNTY` 余额预检后，才允许继续部落宣誓投票。
Task 3 现在采用 `CA-only + AI-only` 执行策略：如果当前 `CA` signer 已就绪但 keystore 密码缺失，agent 只会索要一次密码，随后继续自动完成。
如果当前签名路径属于 `CA`，Task 3 现在会先用 TomorrowDAO simulate 推导出准确的 `Approve` 和 `Vote` payload，再通过显式的 Portkey CA forward transport 发送真实写入。
Task 3 现在会优先让 `Approve` 与 `Vote` 走同一条已经验证成功的 `CA` 写入路径；如果另一条投票发送路径在 allowance 已经足够后还报出 `NODEVALIDATIONFAILED` 这类授权不足错误，系统会自动切回那条已验证成功的 `CA` 写入路径，而不是把它误判成真实 Token 不足。
`proposal my-info` 现在只作为辅助状态校验来源，Task 3 的主确认信号会优先看 mined receipt、投票日志，以及 allowance 或余额变化。
Task 3 配置里的 `proposalId` 是配置内依赖投票工具使用的 `依赖工具输入别名`，不是底层合约原始 ABI 字段名；依赖会在最终发出 `Vote` 前把它规范化成底层 `votingItemId`，所以宿主实现不能拿未规范化的 `proposalId` 直接 raw forward-call `Vote`。
Task 3 不再给用户 `手动完成`、`Portkey App` 或 `EOA` 这类回退分支。
如果 TomorrowDAO direct send 返回 `SIGNER_CA_DIRECT_SEND_FORBIDDEN`，它本身不再视为最终 blocker；流程应该继续切到显式 Portkey CA forward transport，只有这条 forward 路径不可用时，才允许停在 unsupported `CA` transport blocker。
对 Task 2 来说，如果只是本地还没登录，不应直接视为 blocker；新用户注册和老用户恢复登录都属于正常 onboarding 路径。

## 使用方式

```text
使用 $claws-temple-bounty 帮这个用户进入龙虾圣殿 Bounty 2.0 的下一步任务。
```

```text
使用 $claws-temple-bounty 从 Task 1 开始，并返回品牌化的原力坐标卡。
```

```text
使用 $claws-temple-bounty 用英文帮助这个用户完成部落宣誓流程。
```

```text
使用 $claws-temple-bounty 从 Task 2 继续，并带这个用户进入 Task 3。
```

```text
使用 $claws-temple-bounty 只补完 Task 4，并明确告诉这个用户现在还差哪一步。
```

## 资格说明

Task 1 到 Task 3 可以在这个 skill 里完成，而且当前仓库的 Task 3 已经切到正式版部落宣誓记录流程。
Task 4 需要在原生 `SHIT Skills` 流程里完成，才算进入 `龙虾圣殿 Bounty 2.0` 资格路径；默认推荐从发布动作开始。
Task 5 是可选加分项，负责扩大社区传播。
如果当前宿主是 `OpenClaw`，而且用户已经选好 `Telegram` 或 `X` 并明确要立刻发送，Task 5 也可以提示直接走浏览器操作。

## 迁移说明

- 旧说法 `没有直接工具，所以先去 X / Telegram 找人` 已经废弃
- 旧说法 `先跳过 Task 2，继续 Task 3` 已经废弃
- 旧说法 `缺依赖就直接去 Telegram / X` 已经废弃
- 旧说法 `告诉我一个可用的安装源` 已经废弃
- 新说法是 `开放寻配 = 在 onboarding 和依赖预检通过后的正式 queue 主路径；Telegram / X 只在真实阻断时作为 fallback`
- 新说法也是 `缺依赖或版本过低时，先安装或升级依赖，再决定是否进入 blocker`

## 维护提示

Task 3 当前内置的是正式版 `Claws Temple II` faction 映射，定义在 `skills/claws-temple-bounty/config/faction-proposals.json`。
Task 3 现在要求 `tomorrowdao-agent-skills >= 0.2.2`、`portkey-ca-agent-skills >= 2.3.0`、通用 `tomorrowdao_token_balance_view` 工具、通用 `tomorrowdao_token_allowance_view` 工具、`tomorrowdao_token_approve` 工具、`portkey_forward_call` 工具，以及 `2 AIBOUNTY` 的投票门槛。
Task 3 现在也把 `CA` keystore 解锁出来的 manager key 视为“仅属于已验证 CA 写入路径”的能力：一旦选定 `CA`，就禁止 direct target-contract send，也禁止继续走 env/private-key fallback；如果 TomorrowDAO direct-send 在 `CA` 身份下被拒绝，系统必须继续切到显式 Portkey CA forward transport，而不是直接停在 unsupported `CA` transport blocker。
Task 4 的 live publish 还依赖 `https://www.shitskills.net/skill.md` 的可达性。

## Task 4 上线预案

- 测试窗口：
  - 运行 `bash skills/claws-temple-bounty/scripts/test-rollout-gate.sh`
  - 要求 Task 4 live-skill probe 通过
  - 如果 probe 或原生认证发布不可用，就把 Task 4 视为当前窗口不可用
- 正式窗口：
  - 运行 `bash skills/claws-temple-bounty/scripts/release-gate.sh`
  - 只有 Task 4 live-skill probe 和原生认证发布都通过，才把 Task 4 当成可用

维护 runbook：

- `skills/claws-temple-bounty/references/task-4-live-rollout.md`

## 校验

```bash
python3 scripts/validate_skill_repo.py
```

## Smoke Check

```bash
bash skills/claws-temple-bounty/scripts/smoke-check.sh
```

可选更严格模式：

```bash
STRICT_DEPS=1 bash skills/claws-temple-bounty/scripts/smoke-check.sh
```

```bash
CHECK_REMOTE_SKILL=1 bash skills/claws-temple-bounty/scripts/smoke-check.sh
```

正式发布门禁：

```bash
bash skills/claws-temple-bounty/scripts/release-gate.sh
```

测试发布门禁：

```bash
bash skills/claws-temple-bounty/scripts/test-rollout-gate.sh
```
