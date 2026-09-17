"use client";

import React, { useState } from "react";
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Shield, FileText, CheckCircle2 } from "lucide-react";

export interface BoundingBoxHighlight {
  page: number;
  bbox: number[]; // [x0, y0, x1, y1]
  label?: string;
  type?: "citation" | "ocr" | "redaction";
}

interface PDFViewerProps {
  documentId?: string;
  fileName?: string;
  pageCount?: number;
  activeHighlights?: BoundingBoxHighlight[];
  onPageChange?: (page: number) => void;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  documentId,
  fileName = "Document.pdf",
  pageCount = 3,
  activeHighlights = [],
  onPageChange,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);

  const handlePrev = () => {
    if (currentPage > 1) {
      setCurrentPage((p) => {
        const next = p - 1;
        onPageChange?.(next);
        return next;
      });
    }
  };

  const handleNext = () => {
    if (currentPage < pageCount) {
      setCurrentPage((p) => {
        const next = p + 1;
        onPageChange?.(next);
        return next;
      });
    }
  };

  const pageHighlights = activeHighlights.filter((h) => h.page === currentPage);

  return (
    <div className="flex flex-col h-full rounded-xl border border-surface-border bg-surface/50 overflow-hidden shadow-sm">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-surface-border bg-surface px-4 py-2 text-sm text-gray-700 dark:text-gray-300">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-accent" />
          <span className="font-medium max-w-[200px] truncate text-gray-900 dark:text-white">{fileName}</span>
          <span className="rounded bg-surface-border px-2 py-0.5 text-xs text-gray-600 dark:text-gray-400 font-mono">
            {pageCount} pages
          </span>
        </div>

        {/* Page Selector */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrev}
            disabled={currentPage <= 1}
            className="rounded p-1 text-gray-500 hover:bg-surface-border hover:text-gray-900 dark:hover:text-white disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
            Page {currentPage} of {pageCount}
          </span>
          <button
            onClick={handleNext}
            disabled={currentPage >= pageCount}
            className="rounded p-1 text-gray-500 hover:bg-surface-border hover:text-gray-900 dark:hover:text-white disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom((z) => Math.max(50, z - 10))}
            className="rounded p-1 text-gray-500 hover:bg-surface-border hover:text-gray-900 dark:hover:text-white"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="font-mono text-xs text-gray-800 dark:text-gray-200">{zoom}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(200, z + 10))}
            className="rounded p-1 text-gray-500 hover:bg-surface-border hover:text-gray-900 dark:hover:text-white"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* PDF Canvas Viewport with Bounding Box Overlays */}
      <div className="relative flex-1 overflow-auto bg-slate-100 dark:bg-[#0A0F1D] p-6 flex justify-center items-start transition-colors">
        <div
          style={{ width: `${(595 * zoom) / 100}px`, height: `${(842 * zoom) / 100}px` }}
          className="relative bg-white text-gray-900 rounded-sm shadow-2xl p-8 select-text transition-all duration-150 overflow-hidden border border-gray-200 dark:border-transparent"
        >
          {/* Document Content Simulation */}
          <div className="space-y-4 text-xs font-serif leading-relaxed text-gray-800">
            <div className="border-b pb-2">
              <h2 className="text-base font-bold text-gray-900">SECURE ENTERPRISE DOCUMENT — PAGE {currentPage}</h2>
              <p className="text-[10px] text-gray-500 font-mono">Confidential Document ID: {documentId || "spdf_doc_sample"}</p>
            </div>
            
            <p>
              This document is processed under zero-trust ephemeral memory containment. All vector embeddings,
              lexical tokens, and cryptographic keys are isolated on a per-session basis.
            </p>

            <div className="rounded bg-gray-50 border p-3 font-mono text-[11px] text-gray-700">
              <p className="font-semibold text-gray-900 mb-1">Audit Compliance Section {currentPage}.1</p>
              <p>
                Strict verification rules ensure that answers generated through the Hybrid RAG engine
                are cross-checked with Reciprocal Rank Fusion against sparse and dense indexes.
              </p>
            </div>

            <p>
              All sensitive entities, including Social Security Numbers, corporate credentials, and credit cards,
              are scrubbed using deep raster burn-in and font glyph removal.
            </p>
          </div>

          {/* Interactive Dynamic Bounding Box Highlight Overlays */}
          {pageHighlights.map((hl, idx) => {
            const scale = zoom / 100;
            const x0 = (hl.bbox[0] || 40) * scale;
            const y0 = (hl.bbox[1] || 150) * scale;
            const width = Math.max(120, ((hl.bbox[2] || 300) - (hl.bbox[0] || 40)) * scale);
            const height = Math.max(40, ((hl.bbox[3] || 200) - (hl.bbox[1] || 150)) * scale);

            const isCitation = hl.type === "citation" || !hl.type;
            const isRedaction = hl.type === "redaction";

            return (
              <div
                key={idx}
                style={{
                  position: "absolute",
                  left: `${x0}px`,
                  top: `${y0}px`,
                  width: `${width}px`,
                  height: `${height}px`,
                }}
                className={`rounded border-2 transition-all duration-200 pointer-events-none ${
                  isRedaction
                    ? "bg-black border-red-500/80"
                    : "bg-cyan-500/20 border-cyan-400 shadow-cyber animate-pulse"
                }`}
              >
                <div
                  className={`absolute -top-5 left-0 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase tracking-wider ${
                    isRedaction ? "bg-red-500 text-white" : "bg-cyan-500 text-black"
                  }`}
                >
                  {hl.label || (isRedaction ? "REDACTION ZONE" : "VERIFIED SOURCE CITATION")}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
