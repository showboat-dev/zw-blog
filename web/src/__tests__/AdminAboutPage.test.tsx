import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, test, vi } from "vitest";
import { AdminAboutPage } from "../pages/AdminAboutPage";

afterEach(() => vi.unstubAllGlobals());

test("saves about markdown", async () => {
  const fetchMock = vi.fn().mockImplementation(async (_url: string, init?: RequestInit) => {
    if (init?.method === "PUT") {
      return { ok: true, status: 200, json: async () => ({ body_md: "你好" }) };
    }
    return { ok: true, status: 200, json: async () => ({ body_md: "" }) };
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<AdminAboutPage />);
  await screen.findByLabelText("正文 Markdown");
  await userEvent.type(screen.getByLabelText("正文 Markdown"), "你好");
  await userEvent.click(screen.getByRole("button", { name: "保存" }));
  expect(await screen.findByText("已保存")).toBeInTheDocument();
});
