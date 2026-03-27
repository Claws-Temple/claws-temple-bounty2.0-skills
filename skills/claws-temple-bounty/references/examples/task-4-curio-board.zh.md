# Task 4 示例（中文）

> 这是一个双层展开示例，用来展示完整输出结构；plain chat 默认不应主动展开维护者详情。

## 普通用户摘要

你现在在 `Task 4：SHIT Skills 原生流程`。

这一项不再用本地阶段机判断完成状态，我会直接把你带进 `SHIT Skills` 的原生流程。

我先确认两件事：

1. 你是否已经有 `SHIT Skills` 账号。
2. 你是否已经有可发布的 `GitHub repo URL`。

如果你还没有账号，我会先带你走原生注册或登录。  
如果你还没有可发布的 `GitHub repo URL`，这一项现在还不能继续。

进入原生发布前，我还会继续收这些字段：

- `title`
- `summary`
- `githubUrl`
- `tags`
- `installType`
- `installCommand` 或 `installUrl`
- 可选 `content`
- 可选 `coverUrl`

这里不会再把 Task 4 包成本地阶段标签。  
我只会告诉你：你当前是在 `SHIT Skills` 的哪个原生动作里，以及下一步还缺什么。

### 原生动作示例

- `注册账号`：还没有账号，需要先完成 email OTP + password 注册。
- `登录`：已有账号，但当前宿主还没有可用登录态。
- `发布`：账号和 `GitHub repo URL` 都已就绪，可以继续填写原生发布字段。
- `评论 / 投票 / 点赞 / 编辑 / 删除`：进入对应的原生平台动作。
- `解析 GitHub SKILL.md`：用平台原生解析动作补全内容。

### 阻断示例

如果你还没有可发布的 `GitHub repo URL`，或者当前宿主无法完成 `SHIT Skills` 的原生登录 / 发布动作，就应该明确告诉你：

`Task 4 现在还不能继续，因为原生流程需要可发布的 GitHub repo 和可用的 SHIT Skills 登录态。等这两个前置条件具备后，我再继续带你进入原生发布动作。`

- `→ 如果这里卡住了，欢迎到 [Telegram 群](https://t.me/+tChFhfxgU6AzYjJl) 贴出你当前的步骤、报错和关键信息，我们可以一起帮你排查。`
- `→ 也可以去 [X / Twitter](https://x.com/aelfblockchain) 发帖求助，带上你当前的状态和卡点，方便社区更快看到并协助你。`

## 维护者详情

- route: `task-4-curio-board`
- live_dependency: `https://www.shitskills.net/skill.md`
- native_publish_required_fields: `title`, `summary`, `githubUrl`, `tags`, `installType`, `installCommand|installUrl`
