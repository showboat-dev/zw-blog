import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { TagsPage } from "../pages/TagsPage";

afterEach(() => vi.unstubAllGlobals());

test("lists public tags and counts", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ items: [{ name: "技术", slug: "tech", article_count: 2 }] }),
    }),
  );
  render(
    <MemoryRouter>
      <TagsPage />
    </MemoryRouter>,
  );
  expect(await screen.findByText(/技术/)).toBeInTheDocument();
  expect(screen.getByText(/2/)).toBeInTheDocument();
});
