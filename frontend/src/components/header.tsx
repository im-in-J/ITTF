"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Newspaper, BarChart3, Settings, BookmarkCheck } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "피드", icon: Newspaper },
  { href: "/trends", label: "트렌드", icon: BarChart3 },
  { href: "/scrapbook", label: "스크랩", icon: BookmarkCheck },
  { href: "/admin", label: "관리자", icon: Settings },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-brand-600">ITTF</span>
          <span className="hidden sm:inline text-sm text-gray-500">
            빅테크 AI 트렌드
          </span>
        </Link>
        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:bg-gray-100"
              )}
            >
              <Icon size={16} />
              <span className="hidden sm:inline">{label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
