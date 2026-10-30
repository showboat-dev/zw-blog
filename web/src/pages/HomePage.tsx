import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, type ArticleListItem, type Page } from "../api/client";
import { formatDate } from "../utils/date";

export function HomePage() {
  const [params, setParams] = useSearchParams();
  const page = Number(params.get("page") || "1");
  const [data, setData] = useState<Page<ArticleListItem> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    api<Page<ArticleListItem>>(`/api/articles?page=${page}&page_size=10`)
      .then(setData)
      .catch((err) => {
        console.error("Failed to load articles:", err);
        setError(err.message || "加载失败，请稍后重试");
      });
  }, [page]);

  if (error) return <p className="empty">❌ {error}</p>;
  if (!data) return <p className="empty">加载中</p>;
  if (data.items.length === 0) return <p className="empty">还没有文章</p>;

  return (
    <>
      <ol className="log">
        {data.items.map((item) => (
          <li className="log-item" key={item.slug}>
            <time className="spine">{formatDate(item.published_at)}</time>
            <span className="bookmark" aria-hidden="true" />
            <div>
              <h2>
                <Link to={`/posts/${item.slug}`}>{item.title}</Link>
              </h2>
              <p className="excerpt">{item.excerpt}</p>
              <div className="chips">
                {item.tags.map((tag) => (
                  <Link className="chip" key={tag.slug} to={`/tags/${tag.slug}`}>
                    {tag.name}
                  </Link>
                ))}
              </div>
            </div>
          </li>
        ))}
      </ol>
      {data.total > data.page_size && (
        <p>
          <button
            className="btn"
            type="button"
            disabled={page <= 1}
            onClick={() => setParams({ page: String(page - 1) })}
          >
            上一页
          </button>{" "}
          <button
            className="btn"
            type="button"
            disabled={page * data.page_size >= data.total}
            onClick={() => setParams({ page: String(page + 1) })}
          >
            下一页
          </button>
        </p>
      )}
    </>
  );
}
