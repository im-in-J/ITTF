"use client";

import Link from "next/link";
import { ExternalLink, Star, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Article } from "@/lib/api";

const SCORE_COLORS: Record<number, string> = {
  5: "bg-red-100 text-red-700",
  4: "bg-orange-100 text-orange-700",
  3: "bg-yellow-100 text-yellow-700",
  2: "bg-gray-100 text-gray-600",
  1: "bg-gray-50 text-gray-500",
};

const SOURCE_LABELS: Record<string, string> = {
  official_blog: "공식 블로그",
  media: "미디어",
};

export function ArticleCard({ article }: { article: Article }) {
  const score = article.importance_score ?? 0;
  const title = article.title_ko || article.title_en || "제목 없음";
  const companies = article.company_tags;
  const insights = article.insights;

  return (
    <Link href={`/articles/${article.id}`}>
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-brand-300 hover:shadow-sm transition-all cursor-pointer">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* 상단: 기업 + 소스 + 점수 */}
            <div className="flex items-center gap-2 mb-1.5">
              {companies.map((c) => (
                <span
                  key={c}
                  className="px-2 py-0.5 rounded text-xs font-semibold bg-brand-50 text-brand-700"
                >
                  {c}
                </span>
              ))}
              <span className="text-xs text-gray-400">
                {article.source_name} ·{" "}
                {SOURCE_LABELS[article.source_type] || article.source_type}
              </span>
            </div>

            {/* 제목 */}
            <h3 className="font-semibold text-gray-900 leading-snug mb-1 line-clamp-2">
              {title}
            </h3>

            {/* 원문 제목 (번역본이 있을 때만) */}
            {article.title_ko && article.title_en && (
              <p className="text-xs text-gray-400 mb-2 line-clamp-1">
                {article.title_en}
              </p>
            )}

            {/* 인사이트 요약 */}
            {insights?.summary && (
              <p className="text-sm text-gray-600 line-clamp-2">
                {insights.summary}
              </p>
            )}

            {/* 선정 사유 */}
            {!insights?.summary && article.evaluation_reason && (
              <p className="text-sm text-gray-500 line-clamp-1">
                {article.evaluation_reason}
              </p>
            )}
          </div>

          {/* 중요도 점수 */}
          <div
            className={cn(
              "flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg",
              SCORE_COLORS[score] || "bg-gray-100 text-gray-500"
            )}
          >
            {score}
          </div>
        </div>

        {/* 하단: 날짜 + 태그 */}
        <div className="flex items-center gap-2 mt-3 text-xs text-gray-400">
          {article.crawled_at && (
            <span>
              {new Date(article.crawled_at).toLocaleDateString("ko-KR")}
            </span>
          )}
          {article.category_tags.map((tag) => (
            <span
              key={tag}
              className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-500"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </Link>
  );
}
