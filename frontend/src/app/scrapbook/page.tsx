"use client";

import { BookmarkCheck } from "lucide-react";

export default function ScrapbookPage() {
  return (
    <div className="text-center py-20">
      <BookmarkCheck size={48} className="mx-auto text-gray-300 mb-4" />
      <h1 className="text-xl font-bold text-gray-700 mb-2">내 스크랩</h1>
      <p className="text-gray-500">
        Phase 3에서 Google 로그인 연동 후 개인 스크랩 기능이 활성화됩니다.
      </p>
    </div>
  );
}
