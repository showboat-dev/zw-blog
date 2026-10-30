import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type ArticleListItem, type Page, type Tag } from "../api/client";
import { formatDate } from "../utils/date";

export function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  useEffect(() => {
    api<{ items: Tag[] }>("/api/tags").then((data) => setTags(data.items));
  }, []);
  return (
    <>
      <h1 className="page-title">标签</h1>
      <div className="chips">
        {tags.map((tag) => (
          <Link className="chip" key={tag.slug} to={`/tags/${tag.slug}`}>
            {tag.name} · {tag.article_count}
          </Link>
        ))}
      </div>
    </>
  );
}

export function TagArticlesPage() {
  const { slug = "" } = useParams();
  const [tag, setTag] = useState<Tag | null>(null);
  const [items, setItems] = useState<ArticleListItem[]>([]);
  
  useEffect(() => {
    // Fetch tag details to get the display name
    api<{ items: Tag[] }>("/api/tags").then((data) => {
      const found = data.items.find((t) => t.slug === slug);
      setTag(found || null);
    });
    api<Page<ArticleListItem>>(`/api/articles?tag=${slug}`).then((data) => setItems(data.items));
  }, [slug]);
  
  return (
    <>
      <h1 className="page-title">{tag?.name || slug}</h1>
      <ol className="log">
        {items.map((item) => (
          <li className="log-item" key={item.slug}>
            <time className="spine">{formatDate(item.published_at)}</time>
            <span className="bookmark" aria-hidden="true" />
            <div>
              <h2>
                <Link to={`/posts/${item.slug}`}>{item.title}</Link>
              </h2>
            </div>
          </li>
        ))}
      </ol>
    </>
  );
}
