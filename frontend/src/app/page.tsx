"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchArticles, type Article } from "@/lib/api";
import { ArticleCard } from "@/components/article-card";
import { FilterBar } from "@/components/filter-bar";

export default function FeedPage() {
  const [sort, setSort] = useState<"latest" | "importance">("importance");
  const [company, setCompany] = useState<string>("");
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ["articles", sort, company, page],
    queryFn: () =>
      fetchArticles({ sort, company: company || undefined, page, size: 20 }),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">AI 트렌드 피드</h1>
        <div className="text-sm text-gray-500">
          {data ? `총 ${data.total}개 기사` : ""}
        </div>
      </div>

      <FilterBar
        sort={sort}
        onSortChange={setSort}
        company={company}
        onCompanyChange={(c) => {
          setCompany(c);
          setPage(1);
        }}
      />

      {isLoading && (
        <div className="text-center py-12 text-gray-500">로딩 중...</div>
      )}

      {error && (
        <div className="text-center py-12 text-red-500">
          데이터를 불러올 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.
        </div>
      )}

      <div className="space-y-3 mt-4">
        {data?.articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {data && data.total > 20 && (
        <div className="flex justify-center gap-2 mt-8">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-md bg-white border text-sm disabled:opacity-40"
          >
            이전
          </button>
          <span className="px-4 py-2 text-sm text-gray-600">
            {page} / {Math.ceil(data.total / 20)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 20 >= data.total}
            className="px-4 py-2 rounded-md bg-white border text-sm disabled:opacity-40"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
