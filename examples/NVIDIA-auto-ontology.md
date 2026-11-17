# 开源项目速读：NVIDIA/auto-ontology

- 仓库：https://github.com/NVIDIA/auto-ontology
- 简介：Auto Ontology is a Python framework for building semantic, graph-based reasoning layers over data. It enables deterministic query generation, better context retrieval, and more explainable AI for LLM and agent workflows.

## 1. 一句话结论

能用，值得花时间：README 里能对上怎么跑，1.0 万星，说明有人在用，最近也还在动。

## 2. 基本面

- Stars：1.0 万星（10,324）
- Forks：835
- License：Apache-2.0（Apache License 2.0）
- 最近推送：2026-11-08 05:54（Asia/Shanghai），1 天前
- 主语言：Python
- Topics：无
- 默认分支：`main`
- 创建时间：2026-04-28 05:45（Asia/Shanghai），约 6 个月前
- Watchers：47
- 开放 Issue：88
- 最新 Release：暂无（或没有打过正式版）
- 根目录关键文件：`.env.example`、`Dockerfile`、`LICENSE`、`Makefile`、`README.md`、`docker-compose.yml`、`pyproject.toml`

## 3. 怎么跑

### 摘自 README：Quickstart

This runs Auto-Ontology with Docker Compose against Wide World Importers,
Microsoft's sample sales database. You need Docker with Compose v2,
[uv](https://docs.astral.sh/uv/), and an NVIDIA API key (`nvapi-...`) from
[build.nvidia.com](https://build.nvidia.com).

1. Clone the repository and create `.env`:

   ```bash
   git clone https://github.com/NVIDIA/auto-ontology.git && cd auto-ontology
   cp .env.example .env
   ```

   Then set these values in `.env`:

   ```dotenv
   DEFAULT_MODELS_API_KEY=nvapi-...
   AUTH_SECRET=<a long random string, e.g. from openssl rand -base64 32>
   APP_URL=http://localhost:3000
   POSTGRES_PASSWORD=<a new password>
   CONNECTION_STRINGS=postgresql://postgres:<the same password>@postgres:5432/wideworldimporters
   AUTO_ONTOLOGY_ADMIN_PASSWORD=<a new password>
   PGADMIN_PASSWORD=<a new password>
   ```

   Compose publishes Postgres, pgAdmin, and the web app on the host, so replace
   each default password before you start it. `.env.example` also sets an API
   key per model role: replace each `nvapi-your-api-key-here` with your key, or
   delete those lines so they fall back to `DEFAULT_MODELS_API_KEY`.

2. Start Postgres and load the sample database. The seed script lives in
   auto-ontology-eval; pass it the Postgres password you set:

   ```bash
   docker compose up -d --wait postgres
   git clone https://github.com/NVIDIA/auto-ontology-eval.git ../auto-ontology-eval
   (cd ../auto-ontology-eval && uv sync && cp .env.example .env && \
     POSTGRES_PASSWORD='<the same password>' \
     uv run python scripts/seed/seed_wwi.py --database-name wideworldimporters --drop)
   ```

3. Build and start the rest of the stack:

   ```bash
   docker compose up -d --build
   ```

…（后续已截断，完整步骤见原 README）

关键命令（启发式抽取，请对照原 README）：

```
git clone https://github.com/NVIDIA/auto-ontology.git && cd auto-ontology
docker compose up -d --wait postgres
git clone https://github.com/NVIDIA/auto-ontology-eval.git ../auto-ontology-eval
uv run python scripts/seed/seed_wwi.py --database-name wideworldimporters --drop
docker compose up -d --build
```

## 4. 风险点

- 许可：Apache-2.0 属于宽松许可，二次开发和商用相对省心（仍建议核对原文）。
- 维护活跃度：最近推送在 1 天前，目前看起来活跃。
- 根目录有环境变量样例（如 .env.example），运行前多半要自己配密钥。
- 生产可用性边界：先当可演示的工具/PoC 来用；没看到明确的生产承诺前，不要默认它稳定。

## 5. 公众号素材分

**5/5**（面向「风子开始读书」这类 AI 资讯号）

热度高（1.0 万星）；和 Agent / 模型工具链相关，贴「风子开始读书」选题；开源可跑的路径相对清楚；近期仍在更新，适合写时效稿

标题候选：NVIDIA Auto Ontology：已有 1.0 万星，Auto Ontology is a Python framework for building semantic, graph-based…
