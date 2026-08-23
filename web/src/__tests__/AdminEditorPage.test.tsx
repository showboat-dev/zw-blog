import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { AdminEditorPage } from "../pages/AdminEditorPage";

afterEach(() => vi.unstubAllGlobals());

test("renders editor actions", () => {
  render(
    <MemoryRouter>
      <AdminEditorPage />
    </MemoryRouter>,
  );
  expect(screen.getByRole("button", { name: "保存草稿" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "发布" })).toBeInTheDocument();
  expect(screen.getByLabelText("正文 Markdown")).toBeInTheDocument();
  expect(screen.getByText("预览")).toBeInTheDocument();
});
