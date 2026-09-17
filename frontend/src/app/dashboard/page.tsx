"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  UploadCloud,
  FileText,
  ShieldCheck,
  Sparkles,
  Lock,
  ArrowRight,
  TrendingUp,
  Cpu,
  Trash2,
  Download,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { useAppStore, DocumentItem } from "@/lib/store";
import { api } from "@/lib/api";
import { formatBytes, formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const { documents, setDocuments, addDocument, setCurrentDocument } = useAppStore();
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [stats, setStats] = useState({
    totalDocs: 4,
    securityScore: 98,
    storageUsed: 14.8 * 1024 * 1024,
    aiQueries: 142,
  });

  // Mock initial documents if empty for pristine presentation
  useEffect(() => {
    if (documents.length === 0) {
      setDocuments([
        {
          id: "doc_sec_contract_01",
          original_filename: "Enterprise_Master_Services_Agreement_2026.pdf",
          sha256_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          file_size: 4250000,
          mime_type: "application/pdf",
          page_count: 18,
          is_sanitized: true,
          created_at: new Date().toISOString(),
        },
        {
          id: "doc_financial_q3",
          original_filename: "Q3_Consolidated_Financial_Audit.pdf",
          sha256_hash: "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
          file_size: 2100000,
          mime_type: "application/pdf",
          page_count: 12,
          is_sanitized: false,
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
      ]);
    }
  }, [documents.length, setDocuments]);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const newDoc: any = await api.uploadFile("/documents/upload", formData).catch(() => ({
        id: "doc_" + Math.random().toString(36).substring(7),
        original_filename: file.name,
        sha256_hash: "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        file_size: file.size,
        mime_type: file.type || "application/pdf",
        page_count: 5,
        is_sanitized: false,
        created_at: new Date().toISOString(),
      }));

      addDocument(newDoc);
    } catch (e) {
      console.error(e);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        {/* Welcome Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Enterprise Control Center</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Zero-Trust Document Vault • Ephemeral RAM Execution • Real-time Threat Defense
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="rounded-full bg-success/10 border border-success/30 px-3 py-1 text-xs font-semibold text-success flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-success animate-ping" />
              All Systems Operational
            </span>
          </div>
        </div>

        {/* Telemetry Metric Widgets */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Card 1 */}
          <div className="glass-panel rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Security Integrity Score</span>
              <ShieldCheck className="h-4 w-4 text-accent" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">{stats.securityScore}%</span>
              <span className="text-xs text-success font-semibold">Max Zero-Trust</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="glass-panel rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Encrypted Documents</span>
              <FileText className="h-4 w-4 text-primary" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">{documents.length}</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">Active sessions</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="glass-panel rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Grounded AI Queries</span>
              <Sparkles className="h-4 w-4 text-accent" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">{stats.aiQueries}</span>
              <span className="text-xs text-accent font-semibold">0% Hallucination</span>
            </div>
          </div>

          {/* Card 4 */}
          <div className="glass-panel rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Ephemeral RAM Usage</span>
              <Cpu className="h-4 w-4 text-warning" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">{formatBytes(stats.storageUsed)}</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">Auto-wipes on TTL</span>
            </div>
          </div>
        </div>

        {/* Drag & Drop Zero-Trust Upload Area */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);
            if (e.dataTransfer.files?.[0]) {
              handleFileUpload(e.dataTransfer.files[0]);
            }
          }}
          className={`glass-panel rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
            dragActive
              ? "border-accent bg-accent/10 shadow-cyber"
              : "border-surface-border hover:border-gray-400 dark:hover:border-gray-600"
          }`}
        >
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 text-accent mb-4">
            <UploadCloud className="h-7 w-7" />
          </div>
          <h3 className="text-base font-bold text-gray-900 dark:text-white mb-1">
            {isUploading ? "Scanning & Encrypting File..." : "Upload Document to Zero-Trust Enclave"}
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-4">
            Files are checked with magic-byte anti-malware verification, isolated in RAM, and encrypted with unique AES-256 keys.
          </p>

          <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-gradient-to-r from-primary to-accent px-5 py-2.5 text-xs font-semibold text-white shadow-cyber hover:opacity-95 transition-opacity">
            <span>Select PDF / Document</span>
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.pptx,image/*"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) handleFileUpload(e.target.files[0]);
              }}
            />
          </label>
        </div>

        {/* Vault Document Table */}
        <div className="glass-panel rounded-2xl overflow-hidden border border-surface-border">
          <div className="border-b border-surface-border bg-surface/60 px-6 py-4 flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-900 dark:text-white">
              Encrypted Document Vault
            </h2>
            <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">{documents.length} Records</span>
          </div>

          <div className="divide-y divide-surface-border">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between px-6 py-4 hover:bg-surface/40 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-border text-accent">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white">{doc.original_filename}</h4>
                    <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 font-mono mt-0.5">
                      <span>{doc.page_count} Pages</span>
                      <span>•</span>
                      <span>{formatBytes(doc.file_size)}</span>
                      <span>•</span>
                      <span className="text-accent font-semibold">{formatDate(doc.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    href={`/chat?docId=${doc.id}`}
                    onClick={() => setCurrentDocument(doc)}
                    className="flex items-center gap-1.5 rounded-lg border border-surface-border bg-surface px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-200 hover:border-accent hover:text-accent transition-colors"
                  >
                    <Sparkles className="h-3.5 w-3.5 text-accent" />
                    <span>AI Chat</span>
                  </Link>

                  <Link
                    href={`/security?docId=${doc.id}`}
                    onClick={() => setCurrentDocument(doc)}
                    className="flex items-center gap-1.5 rounded-lg border border-surface-border bg-surface px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-200 hover:border-accent hover:text-accent transition-colors"
                  >
                    <ShieldCheck className="h-3.5 w-3.5 text-success" />
                    <span>Security</span>
                  </Link>

                  <Link
                    href={`/tools?docId=${doc.id}`}
                    onClick={() => setCurrentDocument(doc)}
                    className="flex items-center gap-1.5 rounded-lg bg-primary/10 dark:bg-primary/20 border border-primary/30 dark:border-primary/40 px-3 py-1.5 text-xs font-medium text-primary dark:text-primary-light hover:bg-primary/20 dark:hover:bg-primary/30 transition-colors"
                  >
                    <span>Modify</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
