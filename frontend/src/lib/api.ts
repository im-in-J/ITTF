const API_BASE = "/api";

async function fetcher<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`API 오류: ${res.status}`);
  return res.json();
}

// === 기사 ===

export interface Article {
  id: string;
  title_en: string | null;
  title_ko: string | null;
  body_en?: string | null;
  body_ko?: string | null;
  url: string;
  source_name: string;
  source_type: string;
  company_tags: string[];
  category_tags: string[];
  importance_score: number | null;
  evaluation_reason: string | null;
  insights: {
    summary?: string;
    partnership_relevance?: string;
    competitor_impact?: string;
    market_signal?: string;
    physical_ai_applicability?: string;
    action_item?: string;
  } | null;
  published_at: string | null;
  crawled_at: string | null;
}

export interface ArticlesResponse {
  total: number;
  page: number;
  size: number;
  articles: Article[];
}

export function fetchArticles(params: {
  sort?: string;
  company?: string;
  source_type?: string;
  min_score?: number;
  page?: number;
  size?: number;
}) {
  const query = new URLSearchParams();
  if (params.sort) query.set("sort", params.sort);
  if (params.company) query.set("company", params.company);
  if (params.source_type) query.set("source_type", params.source_type);
  if (params.min_score) query.set("min_score", String(params.min_score));
  if (params.page) query.set("page", String(params.page));
  if (params.size) query.set("size", String(params.size));
  return fetcher<ArticlesResponse>(`/articles?${query}`);
}

export function fetchArticle(id: string) {
  return fetcher<Article>(`/articles/${id}`);
}

// === 파이프라인 ===

export interface PipelineRun {
  id: string;
  triggered_at: string;
  trigger_type: string;
  status: string;
  total_crawled: number;
  total_selected: number;
  total_translated: number;
  elapsed_seconds: number;
  api_cost_usd: number;
  errors: string[];
}

export function fetchPipelineHistory(limit = 10) {
  return fetcher<{ runs: PipelineRun[] }>(
    `/admin/pipeline/history?limit=${limit}`
  );
}

export function triggerPipeline(useAi = false) {
  return fetch(`${API_BASE}/admin/pipeline/run?use_ai=${useAi}`, {
    method: "POST",
  }).then((r) => r.json());
}

// === 통계 ===

export interface Stats {
  total_articles: number;
  selected_articles: number;
  translated_articles: number;
  by_source: { source: string; count: number }[];
}

export function fetchStats() {
  return fetcher<Stats>("/admin/stats");
}
