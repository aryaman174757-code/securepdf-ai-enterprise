"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Wrench,
  Sparkles,
  Search,
  ShieldAlert,
  GitFork,
  ScanText,
  FileCheck2,
  Settings,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "PDF Tools (45+)", href: "/tools", icon: Wrench },
  { name: "AI Grounded Chat", href: "/chat", icon: Sparkles },
  { name: "Hybrid Search", href: "/search", icon: Search },
  { name: "Dual OCR Engine", href: "/tools/ocr", icon: ScanText },
  { name: "Security Center", href: "/security", icon: ShieldAlert },
  { name: "Workflow Pipelines", href: "/pipelines", icon: GitFork },
  { name: "Admin Telemetry", href: "/admin", icon: Shield },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-surface-border bg-surface flex flex-col justify-between py-6 transition-colors">
      <div className="space-y-1 px-3">
        <div className="px-3 pb-3 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
          Core Platform
        </div>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-blue-50 dark:bg-accent/10 text-blue-600 dark:text-accent border-l-2 border-blue-600 dark:border-accent font-semibold shadow-sm"
                  : "text-gray-700 dark:text-gray-300 hover:bg-surface-dark hover:text-gray-900 dark:hover:text-white"
              )}
            >
              <Icon className={cn("h-4 w-4", isActive ? "text-blue-600 dark:text-accent" : "text-gray-400 dark:text-gray-400")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Security Status Box */}
      <div className="mx-3 rounded-xl border border-surface-border bg-surface-dark p-3.5 text-xs text-gray-600 dark:text-gray-400 shadow-sm">
        <div className="flex items-center justify-between font-semibold text-gray-900 dark:text-gray-200">
          <span>Zero-Trust Enclave</span>
          <span className="text-success font-mono font-bold">ACTIVE</span>
        </div>
        <div className="mt-2 space-y-1">
          <div className="flex justify-between">
            <span>Isolation</span>
            <span className="text-gray-900 dark:text-gray-200 font-mono">RAM Only</span>
          </div>
          <div className="flex justify-between">
            <span>Key Lifetime</span>
            <span className="text-gray-900 dark:text-gray-200 font-mono">Session TTL</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
