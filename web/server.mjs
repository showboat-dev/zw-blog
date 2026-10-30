import fs from "node:fs";
import http from "node:http";
import https from "node:https";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dist = path.join(__dirname, "dist");
const port = Number(process.env.PORT || 10000);
const apiUpstream = (process.env.API_UPSTREAM || "http://127.0.0.1:8000").replace(/\/$/, "");

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return (
    {
      ".html": "text/html; charset=utf-8",
      ".js": "text/javascript; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".json": "application/json",
      ".svg": "image/svg+xml",
      ".png": "image/png",
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".webp": "image/webp",
      ".ico": "image/x-icon",
      ".woff": "font/woff",
      ".woff2": "font/woff2",
    }[ext] || "application/octet-stream"
  );
}

function rewriteSetCookie(value) {
  // Drop Domain so the browser scopes the cookie to this host (same-origin).
  return value
    .split(/,(?=\s*[^;=]+=[^;]+)/)
    .map((part) =>
      part
        .split(";")
        .filter((attr) => !/^\s*domain=/i.test(attr))
        .join(";"),
    )
    .join(",");
}

function proxyApi(req, res) {
  const target = new URL(req.url, apiUpstream + "/");
  const lib = target.protocol === "https:" ? https : http;
  const headers = { ...req.headers, host: target.host };
  delete headers["connection"];

  const upstream = lib.request(
    target,
    { method: req.method, headers, servername: target.hostname },
    (upRes) => {
      const outHeaders = { ...upRes.headers };
      const raw = upRes.headers["set-cookie"];
      if (raw) {
        const list = Array.isArray(raw) ? raw : [raw];
        outHeaders["set-cookie"] = list.map(rewriteSetCookie);
      }
      res.writeHead(upRes.statusCode || 502, outHeaders);
      upRes.pipe(res);
    },
  );
  upstream.on("error", (err) => {
    res.writeHead(502, { "content-type": "text/plain; charset=utf-8" });
    res.end(`Bad gateway: ${err.message}`);
  });
  req.pipe(upstream);
}

function serveStatic(req, res) {
  const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
  const safe = path.normalize(urlPath).replace(/^(\.\.[/\\])+/, "");
  let filePath = path.join(dist, safe);
  if (!filePath.startsWith(dist)) {
    res.writeHead(403).end("Forbidden");
    return;
  }
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, "index.html");
  }
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(dist, "index.html");
  }
  res.writeHead(200, { "content-type": contentType(filePath) });
  fs.createReadStream(filePath).pipe(res);
}

const server = http.createServer((req, res) => {
  if ((req.url || "").startsWith("/api")) {
    proxyApi(req, res);
    return;
  }
  serveStatic(req, res);
});

server.listen(port, "0.0.0.0", () => {
  console.log(`zw-blog web listening on ${port}, API_UPSTREAM=${apiUpstream}`);
});
