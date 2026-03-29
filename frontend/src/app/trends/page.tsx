"use client";

import { BarChart3 } from "lucide-react";

export default function TrendsPage() {
  return (
    <div className="text-center py-20">
      <BarChart3 size={48} className="mx-auto text-gray-300 mb-4" />
      <h1 className="text-xl font-bold text-gray-700 mb-2">
        주간 트렌드 리포트
      </h1>
      <p className="text-gray-500">
        Phase 2에서 Insight Agent가 생성한 주간 트렌드 리포트가 여기에
        표시됩니다.
      </p>
    </div>
  );
}
