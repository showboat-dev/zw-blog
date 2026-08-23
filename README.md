# zw-blog

个人博客：Vite + React 前台，FastAPI 后台，SQLite。文档见 `docs/`。

## 本地开发

```bash
cp .env.example .env
cd api
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8000
```

健康检查：`GET http://127.0.0.1:8000/api/health`

```bash
docker compose up --build
```

Compose 只有 `web` 与 `api`，数据在 named volume `blog_data`。
