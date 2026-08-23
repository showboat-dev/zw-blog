import { useEffect, useState } from "react";
import { api } from "../api/client";
import { MarkdownView } from "../components/MarkdownView";

export function AboutPage() {
  const [body, setBody] = useState<string | null>(null);
  useEffect(() => {
    api<{ body_md: string }>("/api/about").then((data) => setBody(data.body_md));
  }, []);
  if (body === null) return <p className="empty">加载中</p>;
  if (!body.trim()) return <p className="empty">作者还没有写介绍</p>;
  return (
    <article className="article">
      <span className="spine" aria-hidden="true">
        关于
      </span>
      <span className="bookmark" aria-hidden="true" />
      <div>
        <h1>关于</h1>
        <MarkdownView source={body} />
      </div>
    </article>
  );
}
