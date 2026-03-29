"use client";

import { cn } from "@/lib/utils";

const COMPANIES = [
  "Microsoft",
  "Google",
  "Apple",
  "Meta",
  "Nvidia",
  "OpenAI",
  "Tesla",
  "Anthropic",
  "Mistral AI",
  "Perplexity",
  "Amazon",
];

interface FilterBarProps {
  sort: "latest" | "importance";
  onSortChange: (sort: "latest" | "importance") => void;
  company: string;
  onCompanyChange: (company: string) => void;
}

export function FilterBar({
  sort,
  onSortChange,
  company,
  onCompanyChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-3">
      {/* 정렬 토글 */}
      <div className="flex rounded-lg border border-gray-200 overflow-hidden">
        <button
          onClick={() => onSortChange("importance")}
          className={cn(
            "px-3 py-1.5 text-sm font-medium transition-colors",
            sort === "importance"
              ? "bg-brand-600 text-white"
              : "bg-white text-gray-600 hover:bg-gray-50"
          )}
        >
          중요도순
        </button>
        <button
          onClick={() => onSortChange("latest")}
          className={cn(
            "px-3 py-1.5 text-sm font-medium transition-colors",
            sort === "latest"
              ? "bg-brand-600 text-white"
              : "bg-white text-gray-600 hover:bg-gray-50"
          )}
        >
          최신순
        </button>
      </div>

      {/* 기업 필터 */}
      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => onCompanyChange("")}
          className={cn(
            "px-2.5 py-1 rounded-full text-xs font-medium transition-colors",
            company === ""
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          )}
        >
          전체
        </button>
        {COMPANIES.map((c) => (
          <button
            key={c}
            onClick={() => onCompanyChange(c === company ? "" : c)}
            className={cn(
              "px-2.5 py-1 rounded-full text-xs font-medium transition-colors",
              company === c
                ? "bg-brand-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            {c}
          </button>
        ))}
      </div>
    </div>
  );
}
