const base = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  if (response.status === 204) {
    return undefined as T;
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.error?.code ?? "ERROR",
      data?.error?.message ?? "请求失败",
    );
  }
  return data as T;
}

export type Tag = { name: string; slug: string; article_count?: number };
export type ArticleListItem = {
  slug: string;
  title: string;
  excerpt: string | null;
  cover_path: string | null;
  published_at: string | null;
  tags: Tag[];
};
export type ArticleDetail = ArticleListItem & { body_md: string; updated_at: string };
export type Page<T> = { items: T[]; page: number; page_size: number; total: number };
export type AdminArticle = {
  id: number;
  slug: string;
  title: string;
  body_md: string;
  excerpt: string | null;
  cover_path: string | null;
  status: string;
  published_at: string | null;
  updated_at: string;
  tags: Tag[];
};
export type CommentItem = {
  id: number;
  github_login: string;
  github_avatar_url: string;
  body: string;
  created_at: string;
};
