"use client";

import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Lock,
  Sparkles,
  Cpu,
  GitFork,
  ScanText,
  FileCheck2,
  ArrowRight,
  Database,
  Terminal,
  FileCode2,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 md:py-24">
      {/* Hero Section */}
      <div className="max-w-5xl text-center space-y-6">
        <div className="inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-4 py-1.5 text-xs font-semibold text-accent shadow-sm dark:shadow-cyber animate-pulse">
          <ShieldCheck className="h-4 w-4" />
          <span>ZERO-TRUST ARCHITECTURE • AES-256 GCM • HYBRID RAG</span>
        </div>

        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-gray-900 dark:text-white leading-tight">
          Intelligent Documents with{" "}
          <span className="cyber-gradient-text">Zero-Trust Security</span>
        </h1>

        <p className="mx-auto max-w-2xl text-base md:text-lg text-gray-600 dark:text-gray-400">
          The production-ready AI PDF platform built for Fortune 500 standards.
          Zero persistent plaintext storage, RAM-only execution, Dual OCR, permanent physical redaction, and hallucination-free document intelligence.
        </p>

        {/* Call to Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-primary to-accent px-6 py-3.5 text-base font-semibold text-white shadow-cyber hover:opacity-95 transition-all transform hover:-translate-y-0.5"
          >
            <span>Launch Platform Dashboard</span>
            <ArrowRight className="h-5 w-5" />
          </Link>

          <Link
            href="/chat"
            className="flex items-center gap-2 rounded-xl border border-surface-border bg-surface/80 px-6 py-3.5 text-base font-semibold text-gray-800 dark:text-gray-200 hover:border-accent hover:text-accent transition-all shadow-sm"
          >
            <Sparkles className="h-5 w-5 text-accent" />
            <span>AI Document Chat</span>
          </Link>
        </div>
      </div>

      {/* Feature Architecture Matrix Grid */}
      <div className="mt-24 grid max-w-6xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Card 1 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group hover:border-accent/50 transition-all">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 text-primary mb-4">
            <Lock className="h-6 w-6 text-accent" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Zero-Trust Cryptography</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            Unique AES-256 keys generated per session/job. Files process in isolated ephemeral workspaces with automatic memory zeroing and malware neutralization.
          </p>
        </div>

        {/* Card 2 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group hover:border-accent/50 transition-all">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/20 text-accent mb-4">
            <Sparkles className="h-6 w-6 text-accent" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Hybrid RAG Intelligence</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            Combines dense vector similarity (BGE-M3) with BM25 sparse search and Reciprocal Rank Fusion. Verified citations cite exact page coordinates with zero hallucinations.
          </p>
        </div>

        {/* Card 3 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group hover:border-accent/50 transition-all">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 text-primary mb-4">
            <ScanText className="h-6 w-6 text-accent" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Dual-Engine OCR & CV</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            Tesseract and PaddleOCR engines powered by OpenCV deskewing, denoising, adaptive thresholding, and perspective correction producing searchable PDFs.
          </p>
        </div>

        {/* Card 4 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group hover:border-accent/50 transition-all">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/20 text-accent mb-4">
            <Cpu className="h-6 w-6 text-accent" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">45+ PDF Tools & Converters</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            Complete asynchronous tool suite: Compress, Merge, Split, Bates Numbering, Compare Visual Diff, Table of Contents, and Universal Office conversions.
          </p>
        </div>

        {/* Card 5 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group hover:border-accent/50 transition-all">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 text-primary mb-4">
            <ShieldCheck className="h-6 w-6 text-accent" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Deep Physical Redaction</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            Not visual overlays. Irreversibly purges text layers, font glyphs, OCR bounding boxes, and burns solid black pixels directly into underlying raster images.
          </p>
        </div>

        {/* Card 6 */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group hover:border-accent/50 transition-all">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/20 text-accent mb-4">
            <GitFork className="h-6 w-6 text-accent" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Visual Workflow Pipelines</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
            Interactive drag-and-drop DAG workflow builder. Chain OCR, Redaction, Compression, and AES encryption with real-time WebSocket progress streaming.
          </p>
        </div>
      </div>
    </div>
  );
}
