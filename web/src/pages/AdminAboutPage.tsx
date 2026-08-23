import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";

export function AdminAboutPage() {
  const [body, setBody] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api<{ body_md: string }>("/api/about").then((data) => setBody(data.body_md));
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await api("/api/admin/about", {
      method: "PUT",
      body: JSON.stringify({ body_md: body }),
    });
    setSaved(true);
  }

  return (
    <>
      <h1 className="page-title">编辑关于我</h1>
      <form onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="about">正文 Markdown</label>
          <textarea id="about" value={body} onChange={(event) => setBody(event.target.value)} />
        </div>
        <button className="btn" type="submit">
          保存
        </button>
        {saved && <p className="meta">已保存</p>}
      </form>
    </>
  );
}
