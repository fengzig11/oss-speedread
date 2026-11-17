# 开源项目速读助手

粘贴一个 GitHub 仓库地址，输出一页中文速读报告：能不能用、怎么跑、风险点、适不适合拿去写「风子开始读书」这类 AI 资讯公众号。

这是本周的最小可跑版本（MVP）：本地命令行，不接支付，不登录也能读公开仓库。

## 环境

- Python 3.10+
- `requests`（见 `requirements.txt`）
- 可选：已登录的 [GitHub CLI](https://cli.github.com/)（`gh`），或环境变量 `GITHUB_TOKEN` / `GH_TOKEN`

未配置 token 时走 GitHub 公开 API（未认证大约每小时 60 次）。频率不够时设置 token 即可。

## 安装

```bash
cd oss-speedread
python3 -m pip install -r requirements.txt
```

## 怎么跑

在项目根目录执行（把仓库加进 `PYTHONPATH` 的最简单方式是就在这里跑）：

```bash
cd oss-speedread
python3 -m speedread https://github.com/NVIDIA/auto-ontology
python3 -m speedread NVIDIA/auto-ontology
python3 -m speedread milind-soni/OpenMausBot --json
```

也支持 `owner/repo`、`https://github.com/owner/repo.git`、带 `/tree/...` 的页面链接。

报告默认打印到标准输出。保存成文件：

```bash
python3 -m speedread NVIDIA/auto-ontology > /tmp/auto-ontology.md
```

`--json` 会输出结构化字段，并附带完整 `markdown`。

## 报告里有什么

1. **一句话结论**：能不能用、值不值得花时间
2. **基本面**：stars、forks、license、最近推送、主语言、Topics，以及最新 Release（如果有）
3. **怎么跑**：从 README 里抽 Install / Quick Start / 安装 等段落；找不到会明确写「README 未写清」
4. **风险点**：许可、维护活跃度、密钥/依赖、生产可用性边界
5. **公众号素材分**：1–5 分 + 一句标题候选（按热度、是否好解释、是否开源可跑的 Agent/工具链来估）

时间一律换算成 Asia/Shanghai 后再显示。

## 自测样例

以下两份是对真实公开仓跑出来的样例，只作格式参考（数字会随仓库变化）：

- [`examples/NVIDIA-auto-ontology.md`](examples/NVIDIA-auto-ontology.md)
- [`examples/milind-soni-OpenMausBot.md`](examples/milind-soni-OpenMausBot.md)

重新生成：

```bash
cd oss-speedread
python3 -m speedread NVIDIA/auto-ontology > examples/NVIDIA-auto-ontology.md
python3 -m speedread milind-soni/OpenMausBot > examples/milind-soni-OpenMausBot.md
```

## 已知局限

- 只读 GitHub 公开仓库；私有仓需要有效 token，而且本 MVP 没有为私有仓单独做权限说明。
- 「怎么跑」是启发式抽取，复杂的多语言文档或纯图片 README 可能抽不准。
- 没有周增星、没有克隆后真跑测试，结论基于 API 元数据 + README 文本。
- 未认证 API 容易撞上频率限制；遇到时设置 `GITHUB_TOKEN` 再试。
- 公众号打分是规则粗估，用来过滤选题，不是编辑判断的替代。

## 许可

MIT
