# 开源项目速读：milind-soni/OpenMausBot

- 仓库：https://github.com/milind-soni/OpenMausBot
- 简介：Open-source Grok Bot alternative with a virtual machine that bots can use
- 主页：https://www.mausbot.com/

## 1. 一句话结论

能用，值得花时间：README 里能对上怎么跑，1.8 万星，说明有人在用，最近也还在动。

## 2. 基本面

- Stars：1.8 万星（18,152）
- Forks：2,530
- License：Apache-2.0（Apache License 2.0）
- 最近推送：2026-11-09 05:59（Asia/Shanghai），今天
- 主语言：TypeScript
- Topics：`ai-agents`、`claude-code`、`codex`、`computer-use`、`docker`、`electron`、`grok`、`grok-bot`、`grok-bot-alternative`、`self-hosted`、`typescript`
- 默认分支：`main`
- 创建时间：2026-08-12 02:58（Asia/Shanghai），约 2 个月前
- Watchers：45
- 开放 Issue：825
- 最新 Release：[OpenMausBot 0.1.149](https://github.com/milind-soni/OpenMausBot/releases/tag/v0.1.149)（2026-11-08 20:36（Asia/Shanghai），今天）
- 根目录关键文件：`.env.example`、`Dockerfile`、`LICENSE`、`README.md`、`package.json`

## 3. 怎么跑

### 摘自 README：Quick start

**Released builds ([latest release](https://github.com/milind-soni/OpenMausBot/releases/latest)):** the harness server is embedded, so no separate server setup is required.

| | Download | Install |
|---|---|---|
| **macOS** (Apple silicon) | [OpenMausBot.dmg](https://github.com/milind-soni/OpenMausBot/releases/latest/download/OpenMausBot.dmg) | Drag it to Applications, open it. Signed & notarized. |
| **macOS** (Intel) | [OpenMausBot-intel.dmg](https://github.com/milind-soni/OpenMausBot/releases/latest/download/OpenMausBot-intel.dmg) | Same app, built for Intel Macs. Signed & notarized. |
| **Windows** (x64) | [OpenMausBot-setup.exe](https://github.com/milind-soni/OpenMausBot/releases/latest/download/OpenMausBot-setup.exe) | Run it — one-click, per-user, no admin rights. The installer isn't code-signed yet, so SmartScreen shows "unknown publisher": **More info → Run anyway**. |
| **Ubuntu 24.04** (x64) | [OpenMausBot-amd64.deb](https://github.com/milind-soni/OpenMausBot/releases/latest/download/OpenMausBot-amd64.deb) · [OpenMausBot.AppImage](https://github.com/milind-soni/OpenMausBot/releases/latest/download/OpenMausBot.AppImage) | Install the `.deb` with APT (recommended), or make the AppImage executable and run it. Beta; GNOME is the supported desktop. |

See the [Ubuntu Desktop guide](docs/linux-desktop.md) for installation, capabilities, and troubleshooting.
Any desktop build can also pair as a client to another Windows, macOS, or Ubuntu host over Tailscale; see [desktop-to-desktop companion mode](docs/desktop-companion.md).


**From source:**

```sh
git clone https://github.com/milind-soni/OpenMausBot && cd OpenMausBot
pnpm install

pnpm dev:server    # harness server → 127.0.0.1:8799
pnpm dev           # app → http://127.0.0.1:5199

…（后续已截断，完整步骤见原 README）

关键命令（启发式抽取，请对照原 README）：

```
git clone https://github.com/milind-soni/OpenMausBot && cd OpenMausBot
pnpm install
pnpm dev:server # harness server → 127.0.0.1:8799
pnpm dev # app → http://127.0.0.1:5199
pnpm dev:desktop # Electron shell; keep the two commands above running
pnpm package:mac # macOS: DMG + ZIP; requires Swift/Xcode tools
pnpm package:win # Windows: installer + ZIP
pnpm package:linux # Ubuntu x64: .deb + AppImage + verified CUA runtime
```

## 4. 风险点

- 许可：Apache-2.0 属于宽松许可，二次开发和商用相对省心（仍建议核对原文）。
- 维护活跃度：最近推送就在今天，目前看起来活跃。
- 目前有 825 个开放 Issue，社区负担不轻，踩坑成本可能偏高。
- 根目录有环境变量样例（如 .env.example），运行前多半要自己配密钥。
- 生产可用性边界：先当可演示的工具/PoC 来用；没看到明确的生产承诺前，不要默认它稳定。

## 5. 公众号素材分

**5/5**（面向「风子开始读书」这类 AI 资讯号）

热度高（1.8 万星）；和 Agent / 模型工具链相关，贴「风子开始读书」选题；开源可跑的路径相对清楚；有可引用的版本号（v0.1.149）；近期仍在更新，适合写时效稿

标题候选：OpenMausBot：已有 1.8 万星，Open-source Grok Bot alternative with a virtual machine that bots can use
