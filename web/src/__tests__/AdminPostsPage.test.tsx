import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { AdminPostsPage } from "../pages/AdminPostsPage";

afterEach(() => vi.unstubAllGlobals());

test("lists admin articles and new link", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        items: [
          {
            id: 1,
            slug: "a",
            title: "草稿一篇",
            body_md: "",
            excerpt: null,
            cover_path: null,
            status: "draft",
            published_at: null,
            updated_at: "2026-08-20T00:00:00Z",
            tags: [],
          },
        ],
        page: 1,
        page_size: 10,
        total: 1,
      }),
    }),
  );
  render(
    <MemoryRouter>
      <AdminPostsPage />
    </MemoryRouter>,
  );
  expect(await screen.findByText("草稿一篇")).toBeInTheDocument();
  expect(screen.getByText("新建文章")).toBeInTheDocument();
});
