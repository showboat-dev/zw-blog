import { NavLink, Outlet } from "react-router-dom";

export function Layout({ admin = false }: { admin?: boolean }) {
  return (
    <div className="wrap">
      <header className="site-header">
        <NavLink className="brand" to={admin ? "/admin/posts" : "/"}>
          <span className="brand-mark">ZW</span>
          <span className="brand-name">{admin ? "后台" : "日志"}</span>
        </NavLink>
        <nav>
          {admin ? (
            <>
              <NavLink to="/admin/posts">文章</NavLink>
              <NavLink to="/admin/about">关于我</NavLink>
              <NavLink to="/">站点</NavLink>
            </>
          ) : (
            <>
              <NavLink to="/" end>
                日志
              </NavLink>
              <NavLink to="/tags">标签</NavLink>
              <NavLink to="/search">搜索</NavLink>
              <NavLink to="/about">关于</NavLink>
            </>
          )}
        </nav>
      </header>
      <Outlet />
    </div>
  );
}
