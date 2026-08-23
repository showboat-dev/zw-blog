import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, api } from "../api/client";

export function AdminLoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await api("/api/auth/admin/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      navigate("/admin/posts");
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    }
  }

  return (
    <>
      <h1 className="page-title">后台登录</h1>
      <form className="panel" style={{ maxWidth: "22rem" }} onSubmit={onSubmit}>
        {error && (
          <p className="alert" role="alert">
            {error}
          </p>
        )}
        <div className="field">
          <label htmlFor="username">用户名</label>
          <input
            id="username"
            value={username}
            autoComplete="username"
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">密码</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>
        <button className="btn" type="submit">
          登录
        </button>
      </form>
    </>
  );
}
