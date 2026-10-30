import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type AdminArticle, type Page } from "../api/client";
import { formatDate } from "../utils/date";

const statusLabels: Record<string, string> = {
  draft: "草稿",
  published: "已发布",
};

export function AdminPostsPage() {
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<AdminArticle[]>([]);

  useEffect(() => {
    const query = status ? `?status=${status}` : "";
    api<Page<AdminArticle>>(`/api/admin/articles${query}`).then((data) => setItems(data.items));
  }, [status]);

  return (
    <>
      <h1 className="page-title">文章</h1>
      <p>
        <Link className="link-btn" to="/admin/posts/new">
          新建文章
        </Link>
      </p>
      <div className="filters">
        <button type="button" className={status === "" ? "is-current" : ""} onClick={() => setStatus("")}>
          全部
        </button>
        <button type="button" className={status === "draft" ? "is-current" : ""} onClick={() => setStatus("draft")}>
          草稿
        </button>
        <button
          type="button"
          className={status === "published" ? "is-current" : ""}
          onClick={() => setStatus("published")}
        >
          已发布
        </button>
      </div>
      <table className="admin-table">
        <thead>
          <tr>
            <th>标题</th>
            <th>状态</th>
            <th>更新</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <Link to={`/admin/posts/${item.id}/edit`}>{item.title}</Link>
              </td>
              <td className="status">{statusLabels[item.status] || item.status}</td>
              <td>{formatDate(item.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
