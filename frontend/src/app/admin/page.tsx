"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Play, RefreshCw, Clock, Database, Cpu } from "lucide-react";
import { fetchStats, fetchPipelineHistory, triggerPipeline } from "@/lib/api";

export default function AdminPage() {
  const queryClient = useQueryClient();

  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: fetchStats,
  });

  const { data: history } = useQuery({
    queryKey: ["pipeline-history"],
    queryFn: () => fetchPipelineHistory(5),
  });

  const runPipeline = useMutation({
    mutationFn: () => triggerPipeline(false),
    onSuccess: () => {
      alert("파이프라인 실행이 시작되었습니다.");
      queryClient.invalidateQueries({ queryKey: ["pipeline-history"] });
    },
  });

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">관리자 대시보드</h1>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard
          icon={<Database size={20} />}
          label="총 수집 기사"
          value={stats?.total_articles ?? 0}
        />
        <StatCard
          icon={<Cpu size={20} />}
          label="선별 기사"
          value={stats?.selected_articles ?? 0}
        />
        <StatCard
          icon={<RefreshCw size={20} />}
          label="번역 완료"
          value={stats?.translated_articles ?? 0}
        />
      </div>

      {/* 수동 실행 */}
      <div className="bg-white rounded-lg border p-6 mb-8">
        <h2 className="font-bold mb-3">수동 크롤링 실행</h2>
        <p className="text-sm text-gray-500 mb-4">
          즉시 크롤링 파이프라인을 실행합니다. (규칙 기반 모드)
        </p>
        <button
          onClick={() => runPipeline.mutate()}
          disabled={runPipeline.isPending}
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          <Play size={16} />
          {runPipeline.isPending ? "실행 중..." : "파이프라인 실행"}
        </button>
      </div>

      {/* 소스별 통계 */}
      {stats?.by_source && (
        <div className="bg-white rounded-lg border p-6 mb-8">
          <h2 className="font-bold mb-3">소스별 수집 현황</h2>
          <div className="space-y-2">
            {stats.by_source.map((s) => (
              <div key={s.source} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{s.source}</span>
                <div className="flex items-center gap-2">
                  <div
                    className="h-2 bg-brand-500 rounded-full"
                    style={{
                      width: `${Math.min(200, (s.count / (stats.total_articles || 1)) * 200)}px`,
                    }}
                  />
                  <span className="text-sm text-gray-500 w-12 text-right">
                    {s.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 실행 이력 */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="font-bold mb-3">파이프라인 실행 이력</h2>
        {history?.runs.length === 0 && (
          <p className="text-sm text-gray-500">실행 이력이 없습니다.</p>
        )}
        <div className="space-y-3">
          {history?.runs.map((run) => (
            <div
              key={run.id}
              className="flex items-center justify-between p-3 rounded-lg bg-gray-50"
            >
              <div>
                <div className="flex items-center gap-2 text-sm">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      run.status === "completed"
                        ? "bg-green-500"
                        : run.status === "running"
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                  />
                  <span className="font-medium">
                    {run.trigger_type === "scheduled" ? "정기" : "수동"}
                  </span>
                  <span className="text-gray-400">
                    {new Date(run.triggered_at).toLocaleString("ko-KR")}
                  </span>
                </div>
                <div className="flex gap-4 mt-1 text-xs text-gray-500">
                  <span>수집 {run.total_crawled}</span>
                  <span>선별 {run.total_selected}</span>
                  <span>번역 {run.total_translated}</span>
                </div>
              </div>
              <div className="text-right text-xs text-gray-400">
                <div className="flex items-center gap-1">
                  <Clock size={12} />
                  {run.elapsed_seconds?.toFixed(1)}초
                </div>
                {run.api_cost_usd > 0 && <div>${run.api_cost_usd.toFixed(4)}</div>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center gap-2 text-gray-400 mb-1">{icon}</div>
      <div className="text-2xl font-bold">{value.toLocaleString()}</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  );
}
