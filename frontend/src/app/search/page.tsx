"use client";

import React, { useState } from "react";
import {
  Search,
  Sparkles,
  FileText,
  Layers,
  ArrowRight,
  Filter,
  CheckCircle2,
} from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { PDFViewer, BoundingBoxHighlight } from "@/components/pdf-viewer/PDFViewer";
import { useAppStore } from "@/lib/store";
import { api } from "@/lib/api";

export default function HybridSearchPage() {
  const { currentDocument } = useAppStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState<"hybrid" | "semantic" | "exact" | "clause" | "table">("hybrid");
  const [isSearching, setIsSearching] = useState(false);
  const [activeHighlights, setActiveHighlights] = useState<BoundingBoxHighlight[]>([]);

  const [results, setResults] = useState([
    {
      page: 1,
      chunk_index: 0,
      content: "All cryptographic sessions are protected under AES-256-GCM authenticated cipher with ephemeral zero-trust memory containment.",
      score: 0.965,
      bbox: [50, 160, 480, 220],
      match_type: "Dense + Sparse RRF",
    },
    {
      page: 2,
      chunk_index: 3,
      content: "Strict verification rules ensure that answers generated through the Hybrid RAG engine are cross-checked with Reciprocal Rank Fusion.",
      score: 0.892,
      bbox: [50, 120, 500, 170],
      match_type: "Dense Semantic",
    },
  ]);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const res: any = await api.request("/search/hybrid", {
        method: "POST",
        body: JSON.stringify({
          document_id: currentDocument?.id || "doc_sample",
          query: searchQuery,
          search_mode: searchMode,
          top_k: 10,
        }),
      }).catch(() => null);

      if (res && res.length > 0) {
        setResults(res);
      }
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: Search Explorer */}
        <div className="w-1/2 flex flex-col border-r border-surface-border bg-surface/30 p-8 space-y-6 overflow-y-auto">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2">
              <Search className="h-6 w-6 text-blue-600 dark:text-accent" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">Hybrid Semantic & BM25 Search</h1>
            </div>
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Dense vector embeddings fused with sparse BM25 lexical ranking and Cross-Encoder precision.
            </p>
          </div>

          {/* Search Bar & Mode Selector */}
          <form onSubmit={handleSearch} className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search clauses, terms, or semantic concepts..."
                className="w-full rounded-xl border border-surface-border bg-white dark:bg-background pl-10 pr-24 py-3 text-xs text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:border-blue-500 dark:focus:border-accent focus:outline-none shadow-sm"
              />
              <button
                type="submit"
                disabled={isSearching}
                className="absolute right-2 top-2 rounded-lg bg-gradient-to-r from-primary to-accent px-4 py-1.5 text-xs font-semibold text-white shadow-md hover:opacity-95 disabled:opacity-40 transition-all"
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>

            {/* Mode Pills */}
            <div className="flex flex-wrap gap-2 pt-1">
              {[
                { id: "hybrid", label: "Hybrid (Dense + BM25)" },
                { id: "semantic", label: "Semantic Only" },
                { id: "exact", label: "Exact Keyword" },
                { id: "clause", label: "Clause Match" },
                { id: "table", label: "Table Matrix" },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setSearchMode(m.id as any)}
                  className={`rounded-lg px-3 py-1 text-[11px] font-medium transition-all shadow-sm ${
                    searchMode === m.id
                      ? "bg-blue-50 dark:bg-accent/10 border border-blue-500 dark:border-accent text-blue-600 dark:text-accent font-semibold"
                      : "border border-surface-border bg-surface text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </form>

          {/* Search Results List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <span className="font-semibold uppercase tracking-wider">Ranked Results</span>
              <span className="font-mono text-[10px]">{results.length} Matches Found</span>
            </div>

            {results.map((item, idx) => (
              <div
                key={idx}
                onClick={() =>
                  setActiveHighlights([
                    {
                      page: item.page,
                      bbox: item.bbox,
                      label: `MATCH (PAGE ${item.page}) - SCORE ${Math.round(item.score * 100)}%`,
                      type: "citation",
                    },
                  ])
                }
                className="glass-panel cursor-pointer rounded-xl p-4 border border-surface-border hover:border-blue-500 dark:hover:border-accent hover:shadow-md transition-all"
              >
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2">
                  <div className="flex items-center gap-2 font-mono">
                    <span className="rounded bg-blue-50 dark:bg-accent/10 text-blue-600 dark:text-accent px-2 py-0.5 font-bold">
                      Page {item.page}
                    </span>
                    <span className="text-gray-400 dark:text-gray-500">•</span>
                    <span className="text-gray-700 dark:text-gray-300">{item.match_type}</span>
                  </div>
                  <span className="font-mono text-success font-semibold">
                    Score: {item.score}
                  </span>
                </div>

                <p className="text-xs text-gray-800 dark:text-gray-200 leading-relaxed font-serif">
                  "{item.content}"
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: PDF Viewer with Highlight Overlay */}
        <div className="w-1/2 p-6 flex flex-col">
          <PDFViewer
            documentId={currentDocument?.id || "doc_search"}
            fileName={currentDocument?.original_filename || "Search_Indexed_Doc.pdf"}
            pageCount={currentDocument?.page_count || 8}
            activeHighlights={activeHighlights}
          />
        </div>
      </div>
    </div>
  );
}
