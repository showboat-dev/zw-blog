import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { api } from "../api/client";

export function RequireAdmin() {
  const [ok, setOk] = useState<boolean | null>(null);
  useEffect(() => {
    api("/api/auth/admin/me")
      .then(() => setOk(true))
      .catch(() => setOk(false));
  }, []);
  if (ok === null) return <p className="empty">加载中</p>;
  if (!ok) return <Navigate to="/admin/login" replace />;
  return <Outlet />;
}
