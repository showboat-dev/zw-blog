import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { HomePage } from "../pages/HomePage";

afterEach(() => {
  vi.unstubAllGlobals();
});

test("shows empty copy when there are no posts", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [], page: 1, page_size: 10, total: 0 }),
    }),
  );
  render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>,
  );
  expect(await screen.findByText("还没有文章")).toBeInTheDocument();
});

test("renders published titles", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        items: [
          {
            slug: "hello",
            title: "一篇已发布",
            excerpt: "摘要",
            cover_path: null,
            published_at: "2026-08-20T00:00:00Z",
            tags: [{ name: "技术", slug: "tech" }],
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
      <HomePage />
    </MemoryRouter>,
  );
  expect(await screen.findByText("一篇已发布")).toBeInTheDocument();
});
