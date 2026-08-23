import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type AdminArticle } from "../api/client";
import { MarkdownView } from "../components/MarkdownView";

export function AdminEditorPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [articleId, setArticleId] = useState<number | null>(id ? Number(id) : null);
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [tags, setTags] = useState("");
  const [bodyMd, setBodyMd] = useState("");
  const [status, setStatus] = useState("draft");

  useEffect(() => {
    if (!id) return;
    api<AdminArticle>(`/api/admin/articles/${id}`).then((article) => {
      setArticleId(article.id);
      setTitle(article.title);
      setSlug(article.slug);
      setExcerpt(article.excerpt ?? "");
      setTags(article.tags.map((tag) => tag.name).join(","));
      setBodyMd(article.body_md);
      setStatus(article.status);
    });
  }, [id]);

  async function saveDraft(event?: FormEvent) {
    event?.preventDefault();
    const payload = {
      title,
      slug: slug || null,
      excerpt: excerpt || null,
      body_md: bodyMd,
      tag_names: tags.split(",").map((item) => item.trim()).filter(Boolean),
    };
    if (articleId) {
      await api(`/api/admin/articles/${articleId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    } else {
      const created = await api<AdminArticle>("/api/admin/articles", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setArticleId(created.id);
      navigate(`/admin/posts/${created.id}/edit`, { replace: true });
    }
  }

  async function publish() {
    if (!articleId) await saveDraft();
    const currentId = articleId;
    if (currentId) {
      await api(`/api/admin/articles/${currentId}/publish`, { method: "POST" });
      setStatus("published");
    }
  }

  async function unpublish() {
    if (!articleId) return;
    await api(`/api/admin/articles/${articleId}/unpublish`, { method: "POST" });
    setStatus("draft");
  }

  async function onUpload(file: File) {
    const body = new FormData();
    body.append("file", file);
    const result = await api<{ url: string }>("/api/admin/uploads", { method: "POST", body });
    setBodyMd((current) => `${current}\n\n![](${result.url})\n`);
  }

  return (
    <>
      <h1 className="page-title">编辑文章</h1>
      <form onSubmit={saveDraft}>
        <div className="field">
          <label htmlFor="title">标题</label>
          <input id="title" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </div>
        <div className="field">
          <label htmlFor="slug">短链接</label>
          <input id="slug" value={slug} onChange={(event) => setSlug(event.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="excerpt">摘要</label>
          <input id="excerpt" value={excerpt} onChange={(event) => setExcerpt(event.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="tags">标签（逗号分隔）</label>
          <input id="tags" value={tags} onChange={(event) => setTags(event.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="file">上传配图</label>
          <input
            id="file"
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) void onUpload(file);
            }}
          />
        </div>
        <div className="editor-grid">
          <div className="field">
            <label htmlFor="body">正文 Markdown</label>
            <textarea id="body" value={bodyMd} onChange={(event) => setBodyMd(event.target.value)} />
          </div>
          <div className="panel">
            <p className="meta">预览</p>
            <MarkdownView source={bodyMd} />
          </div>
        </div>
        <p>
          <button className="btn" type="submit">
            保存草稿
          </button>{" "}
          <button className="btn" type="button" onClick={() => void publish()}>
            发布
          </button>{" "}
          {status === "published" && (
            <button className="btn-ghost" type="button" onClick={() => void unpublish()}>
              撤回为草稿
            </button>
          )}
        </p>
      </form>
    </>
  );
}
