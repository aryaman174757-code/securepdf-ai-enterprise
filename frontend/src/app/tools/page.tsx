"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Wrench,
  Layers,
  Minimize2,
  Maximize2,
  RotateCw,
  Crop,
  Sparkles,
  FileText,
  Lock,
  ScanText,
  FileSpreadsheet,
  Presentation,
  Code,
  FileCheck,
  Search,
  ArrowRight,
  ShieldAlert,
  Hash,
  ListOrdered,
  FileImage,
} from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { PDF_TOOLS_CATALOG } from "@/lib/toolsCatalog";

export default function ToolsCatalogPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categories = ["All", "Modification", "Conversion", "Legal & Audit", "Optimization", "Security", "AI & OCR"];

  const filteredTools = PDF_TOOLS_CATALOG.filter((t) => {
    const matchesCategory = selectedCategory === "All" || t.category === selectedCategory;
    const matchesSearch =
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">45+ Enterprise PDF Tools & Converters</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              All tools execute asynchronously under zero-trust ephemeral memory containment.
            </p>
          </div>

          {/* Search Bar */}
          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tools..."
              className="w-full rounded-xl border border-surface-border bg-surface pl-9 pr-4 py-2 text-xs text-gray-900 dark:text-white placeholder-gray-400 focus:border-accent focus:outline-none"
            />
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all ${
                selectedCategory === cat
                  ? "bg-gradient-to-r from-primary to-accent text-white shadow-cyber"
                  : "border border-surface-border bg-surface text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-surface/80"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {filteredTools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link
                key={tool.id}
                href={`/tools/${tool.id}`}
                className="glass-panel rounded-2xl p-5 flex flex-col justify-between group hover:border-accent/50 hover:shadow-cyber transition-all transform hover:-translate-y-0.5"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 dark:bg-primary/20 text-accent group-hover:bg-accent/20 transition-colors">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="rounded-md bg-surface-border px-2 py-0.5 text-[10px] font-mono text-accent">
                      {tool.badge}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-gray-900 dark:text-white group-hover:text-accent transition-colors">
                    {tool.name}
                  </h3>
                  <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 leading-relaxed">{tool.description}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-surface-border/50 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span className="font-mono text-[10px] uppercase text-gray-500">{tool.category}</span>
                  <div className="flex items-center gap-1 text-accent font-medium group-hover:translate-x-1 transition-transform">
                    <span>Open Tool</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
