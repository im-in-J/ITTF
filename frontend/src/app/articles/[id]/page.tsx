"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ExternalLink,
  Bookmark,
  Star,
  Lightbulb,
  TrendingUp,
  Users,
  Crosshair,
  Zap,
} from "lucide-react";
import { fetchArticle } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [viewMode, setViewMode] = useState<"ko" | "en">("ko");

  const { data: article, isLoading } = useQuery({
    queryKey: ["article", id],
    queryFn: () => fetchArticle(id),
  });

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">로딩 중...</div>;
  }

  if (!article || "error" in article) {
    return (
      <div className="text-center py-12 text-red-500">
        기사를 찾을 수 없습니다.
      </div>
    );
  }

  const insights = article.insights;

  return (
    <div className="max-w-3xl mx-auto">
      {/* 뒤로가기 */}
      <Link
        href="/"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft size={16} /> 피드로 돌아가기
      </Link>

      {/* 헤더 */}
      <div className="bg-white rounded-lg border p-6 mb-4">
        <div className="flex items-center gap-2 mb-3">
          {article.company_tags.map((c) => (
            <span
              key={c}
              className="px-2.5 py-0.5 rounded text-sm font-semibold bg-brand-50 text-brand-700"
            >
              {c}
            </span>
          ))}
          <span className="text-sm text-gray-400">
            {article.source_name}
          </span>
          {article.importance_score && (
            <span
              className={cn(
                "ml-auto px-2.5 py-0.5 rounded-full text-sm font-bold",
                article.importance_score >= 4
                  ? "bg-red-100 text-red-700"
                  : "bg-yellow-100 text-yellow-700"
              )}
            >
              {article.importance_score}점
            </span>
          )}
        </div>

        <h1 className="text-xl font-bold mb-1">
          {article.title_ko || article.title_en}
        </h1>
        {article.title_ko && article.title_en && (
          <p className="text-sm text-gray-400 mb-3">{article.title_en}</p>
        )}

        <div className="flex items-center gap-3 text-xs text-gray-400">
          {article.crawled_at && (
            <span>
              수집:{" "}
              {new Date(article.crawled_at).toLocaleDateString("ko-KR")}
            </span>
          )}
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-brand-600 hover:underline"
          >
            원문 보기 <ExternalLink size={12} />
          </a>
        </div>
      </div>

      {/* 선정 사유 */}
      {article.evaluation_reason && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-blue-800 mb-1">
            <Lightbulb size={16} /> 왜 이 기사가 선정되었나?
          </div>
          <p className="text-sm text-blue-700">{article.evaluation_reason}</p>
        </div>
      )}

      {/* 인사이트 */}
      {insights && (
        <div className="bg-white rounded-lg border p-6 mb-4">
          <h2 className="flex items-center gap-2 font-bold mb-4">
            <Star size={18} className="text-yellow-500" /> AI 인사이트
          </h2>
          <div className="space-y-3">
            {insights.summary && (
              <InsightRow
                icon={<Zap size={14} />}
                label="핵심 요약"
                value={insights.summary}
              />
            )}
            {insights.partnership_relevance && (
              <InsightRow
                icon={<Users size={14} />}
                label="파트너십 관련성"
                value={insights.partnership_relevance}
              />
            )}
            {insights.competitor_impact && (
              <InsightRow
                icon={<Crosshair size={14} />}
                label="경쟁사 영향"
                value={insights.competitor_impact}
              />
            )}
            {insights.market_signal && (
              <InsightRow
                icon={<TrendingUp size={14} />}
                label="시장 시그널"
                value={insights.market_signal}
              />
            )}
            {insights.physical_ai_applicability && (
              <InsightRow
                icon={<Zap size={14} />}
                label="현실 세계 적용"
                value={insights.physical_ai_applicability}
              />
            )}
            {insights.action_item && (
              <InsightRow
                icon={<Star size={14} />}
                label="액션 아이템"
                value={insights.action_item}
                highlight
              />
            )}
          </div>
        </div>
      )}

      {/* 본문 */}
      {(article.body_ko || article.body_en) && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center gap-2 mb-4">
            <button
              onClick={() => setViewMode("ko")}
              className={cn(
                "px-3 py-1 rounded text-sm",
                viewMode === "ko"
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600"
              )}
            >
              번역본
            </button>
            <button
              onClick={() => setViewMode("en")}
              className={cn(
                "px-3 py-1 rounded text-sm",
                viewMode === "en"
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600"
              )}
            >
              원문
            </button>
          </div>
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
            {viewMode === "ko"
              ? article.body_ko || "(번역 대기 중)"
              : article.body_en || "(원문 없음)"}
          </div>
        </div>
      )}
    </div>
  );
}

function InsightRow({
  icon,
  label,
  value,
  highlight,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex gap-3 p-3 rounded-lg",
        highlight ? "bg-yellow-50" : "bg-gray-50"
      )}
    >
      <div className="flex-shrink-0 mt-0.5 text-gray-400">{icon}</div>
      <div>
        <div className="text-xs font-semibold text-gray-500 mb-0.5">
          {label}
        </div>
        <div className="text-sm text-gray-700">{value}</div>
      </div>
    </div>
  );
}
