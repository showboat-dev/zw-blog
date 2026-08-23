import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { SearchPage } from "../pages/SearchPage";

afterEach(() => vi.unstubAllGlobals());

test("empty submit does not fetch q and shows hint", async () => {
  const fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
  render(
    <MemoryRouter>
      <SearchPage />
    </MemoryRouter>,
  );
  await userEvent.click(screen.getByRole("button", { name: "搜索" }));
  expect(await screen.findByText("输入关键词")).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});

test("empty results show copy", async () => {
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
      <SearchPage />
    </MemoryRouter>,
  );
  await userEvent.type(screen.getByLabelText("关键词"), "xyz");
  await userEvent.click(screen.getByRole("button", { name: "搜索" }));
  expect(await screen.findByText("没有找到相关文章")).toBeInTheDocument();
});
