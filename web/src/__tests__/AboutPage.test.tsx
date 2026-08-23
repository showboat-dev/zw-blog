import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { AboutPage } from "../pages/AboutPage";

afterEach(() => vi.unstubAllGlobals());

test("shows empty about copy", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ body_md: "" }),
    }),
  );
  render(<AboutPage />);
  expect(await screen.findByText("作者还没有写介绍")).toBeInTheDocument();
});
