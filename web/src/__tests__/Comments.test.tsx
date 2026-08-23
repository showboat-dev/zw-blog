import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { PostPage } from "../pages/PostPage";

afterEach(() => vi.unstubAllGlobals());

function json(status: number, body: unknown) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

const article = {
  slug: "cmt",
  title: "评",
  excerpt: "",
  cover_path: null,
  published_at: "2026-08-20T00:00:00Z",
  updated_at: "2026-08-20T00:00:00Z",
  tags: [],
  body_md: "正文",
};

test("anonymous sees GitHub login and existing comments", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async (url: string) => {
      if (String(url).includes("/comments")) {
        return json(200, {
          items: [
            {
              id: 1,
              github_login: "octocat",
              github_avatar_url: "https://example.com/a.png",
              body: "已有评论",
              created_at: "2026-08-21T00:00:00Z",
            },
          ],
        });
      }
      if (String(url).includes("/api/articles/cmt")) return json(200, article);
      return json(401, { error: { code: "UNAUTHORIZED", message: "未登录" } });
    }),
  );
  render(
    <MemoryRouter initialEntries={["/posts/cmt"]}>
      <Routes>
        <Route path="/posts/:slug" element={<PostPage />} />
      </Routes>
    </MemoryRouter>,
  );
  expect(await screen.findByText("使用 GitHub 登录")).toBeInTheDocument();
  expect(screen.getByText("已有评论")).toBeInTheDocument();
});
