import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, api, type ArticleDetail, type CommentItem } from "../api/client";
import { MarkdownView } from "../components/MarkdownView";

export function PostPage() {
  const { slug = "" } = useParams();
  const [article, setArticle] = useState<ArticleDetail | null>(null);
  const [missing, setMissing] = useState(false);
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [reader, setReader] = useState<{ login: string } | null>(null);
  const [admin, setAdmin] = useState(false);
  const [body, setBody] = useState("");

  useEffect(() => {
    api<ArticleDetail>(`/api/articles/${slug}`)
      .then(setArticle)
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 404) setMissing(true);
      });
    api<{ items: CommentItem[] }>(`/api/articles/${slug}/comments`).then((data) =>
      setComments(data.items),
    );
    api<{ login: string }>("/api/auth/github/me")
      .then(setReader)
      .catch(() => setReader(null));
    api("/api/auth/admin/me")
      .then(() => setAdmin(true))
      .catch(() => setAdmin(false));
  }, [slug]);

  if (missing) return <p className="empty">文章不存在</p>;
  if (!article) return <p className="empty">加载中</p>;

  async function onComment(event: FormEvent) {
    event.preventDefault();
    const created = await api<CommentItem>(`/api/articles/${slug}/comments`, {
      method: "POST",
      body: JSON.stringify({ body }),
    });
    setComments((current) => [...current, created]);
    setBody("");
  }

  async function onDelete(id: number) {
    await api(`/api/admin/comments/${id}`, { method: "DELETE" });
    setComments((current) => current.filter((item) => item.id !== id));
  }

  return (
    <>
      <article className="article">
        <time className="spine">{article.published_at}</time>
        <span className="bookmark" aria-hidden="true" />
        <div>
          <h1>{article.title}</h1>
          <div className="chips">
            {article.tags.map((tag) => (
              <Link className="chip" key={tag.slug} to={`/tags/${tag.slug}`}>
                {tag.name}
              </Link>
            ))}
          </div>
          <MarkdownView source={article.body_md} />
        </div>
      </article>
      <section className="comments">
        <h2>评论</h2>
        {reader ? (
          <form onSubmit={onComment}>
            <div className="field">
              <label htmlFor="comment-body">评论</label>
              <textarea
                id="comment-body"
                value={body}
                maxLength={2000}
                onChange={(event) => setBody(event.target.value)}
                required
              />
            </div>
            <button className="btn" type="submit">
              发表评论
            </button>
          </form>
        ) : (
          <p>
            <a className="link-btn" href={`/api/auth/github?next=/posts/${slug}`}>
              使用 GitHub 登录
            </a>
          </p>
        )}
        {comments.map((item) => (
          <div className="comment" key={item.id}>
            <img className="avatar" src={item.github_avatar_url} alt="" />
            <div>
              <div className="meta">
                {item.github_login} · {item.created_at}
              </div>
              <p>{item.body}</p>
            </div>
            {admin && (
              <button className="btn-ghost" type="button" onClick={() => onDelete(item.id)}>
                删除评论
              </button>
            )}
          </div>
        ))}
      </section>
    </>
  );
}
