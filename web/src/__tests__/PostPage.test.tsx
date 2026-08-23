import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { PostPage } from "../pages/PostPage";

afterEach(() => {
  vi.unstubAllGlobals();
});

function json(status: number, body: unknown) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  };
}

test("shows missing copy for unknown slug", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async (url: string) => {
      if (String(url).includes("/api/articles/missing") && !String(url).includes("comments")) {
        return json(404, { error: { code: "NOT_FOUND", message: "文章不存在" } });
      }
      if (String(url).includes("comments")) return json(200, { items: [] });
      return json(401, { error: { code: "UNAUTHORIZED", message: "未登录" } });
    }),
  );
  render(
    <MemoryRouter initialEntries={["/posts/missing"]}>
      <Routes>
        <Route path="/posts/:slug" element={<PostPage />} />
      </Routes>
    </MemoryRouter>,
  );
  expect(await screen.findByText("文章不存在")).toBeInTheDocument();
});

test("does not execute script tags in markdown", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async (url: string) => {
      if (String(url).includes("/comments")) return json(200, { items: [] });
      if (String(url).includes("/api/articles/safe")) {
        return json(200, {
          slug: "safe",
          title: "安全",
          excerpt: "",
          cover_path: null,
          published_at: "2026-08-20T00:00:00Z",
          updated_at: "2026-08-20T00:00:00Z",
          tags: [],
          body_md: "<script>window.__hacked=1</script>\n\n正常段落",
        });
      }
      return json(401, { error: { code: "UNAUTHORIZED", message: "未登录" } });
    }),
  );
  render(
    <MemoryRouter initialEntries={["/posts/safe"]}>
      <Routes>
        <Route path="/posts/:slug" element={<PostPage />} />
      </Routes>
    </MemoryRouter>,
  );
  expect(await screen.findByText("正常段落")).toBeInTheDocument();
  expect(document.querySelector("script")).toBeNull();
  expect((window as unknown as { __hacked?: number }).__hacked).toBeUndefined();
});
