# Render: same-origin admin cookies

`*.onrender.com` is on the public suffix list, so a cookie set by `zw-blog-backend.onrender.com` is cross-site for `zw-blog-site.onrender.com`. Many browsers block that cookie; login then looks like it resets the form.

The web service runs `web/server.mjs`, which serves the SPA and proxies `/api/*` to `API_UPSTREAM`. Build with empty `VITE_API_BASE_URL` so the browser calls `/api/...` on the site host.

## Render env (zw-blog-site)

- `VITE_API_BASE_URL` = (empty)
- `API_UPSTREAM` = `https://zw-blog-backend.onrender.com`
- Docker command: use image default `node server.mjs` (do not override with `npx serve`)

## Local

`npm run dev` still talks to the API via Vite proxy / `VITE_API_BASE_URL` as before. For a production-like check: build with empty base URL, set `API_UPSTREAM`, run `npm start`.
