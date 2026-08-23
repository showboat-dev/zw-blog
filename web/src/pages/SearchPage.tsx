import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { api, type ArticleListItem, type Page } from "../api/client";

export function SearchPage() {
  const [q, setQ] = useState("");
  const [hint, setHint] = useState("");
  const [items, setItems] = useState<ArticleListItem[] | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!q.trim()) {
      setHint("输入关键词");
      setItems(null);
      return;
    }
    setHint("");
    const data = await api<Page<ArticleListItem>>(`/api/articles?q=${encodeURIComponent(q.trim())}`);
    setItems(data.items);
  }

  return (
    <>
      <h1 className="page-title">搜索</h1>
      <form onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="q">关键词</label>
          <input id="q" value={q} onChange={(event) => setQ(event.target.value)} />
        </div>
        <button className="btn" type="submit">
          搜索
        </button>
      </form>
      {hint && (
        <p className="empty" role="alert">
          {hint}
        </p>
      )}
      {items && items.length === 0 && <p className="empty">没有找到相关文章</p>}
      {items && items.length > 0 && (
        <ol className="log">
          {items.map((item) => (
            <li className="log-item" key={item.slug}>
              <span className="spine">{item.published_at}</span>
              <span className="bookmark" aria-hidden="true" />
              <div>
                <h2>
                  <Link to={`/posts/${item.slug}`}>{item.title}</Link>
                </h2>
              </div>
            </li>
          ))}
        </ol>
      )}
    </>
  );
}
