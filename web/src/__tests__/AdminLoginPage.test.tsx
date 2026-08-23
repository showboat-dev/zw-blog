import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, expect, test, vi } from "vitest";
import { AdminLoginPage } from "../pages/AdminLoginPage";

afterEach(() => vi.unstubAllGlobals());

test("shows generic login error", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: { code: "UNAUTHORIZED", message: "用户名或密码不正确" } }),
    }),
  );
  render(
    <MemoryRouter>
      <AdminLoginPage />
    </MemoryRouter>,
  );
  await userEvent.type(screen.getByLabelText("用户名"), "a");
  await userEvent.type(screen.getByLabelText("密码"), "b");
  await userEvent.click(screen.getByRole("button", { name: "登录" }));
  expect(await screen.findByText("用户名或密码不正确")).toBeInTheDocument();
});

test("unauthenticated admin posts route goes to login via RequireAdmin", async () => {
  const { RequireAdmin } = await import("../pages/RequireAdmin");
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: { code: "UNAUTHORIZED", message: "未登录" } }),
    }),
  );
  render(
    <MemoryRouter initialEntries={["/admin/posts"]}>
      <Routes>
        <Route path="/admin/login" element={<p>登录页</p>} />
        <Route element={<RequireAdmin />}>
          <Route path="/admin/posts" element={<p>后台列表</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
  expect(await screen.findByText("登录页")).toBeInTheDocument();
});
