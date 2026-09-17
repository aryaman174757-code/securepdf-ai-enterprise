"use client";

import React, { useState } from "react";
import {
  Play,
  Plus,
  Trash2,
  CheckCircle2,
  Clock,
  Sparkles,
  Lock,
  FileSearch,
  Layers,
  ArrowRight,
} from "lucide-react";

export interface NodeItem {
  id: string;
  type: string;
  name: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  config: Record<string, any>;
}

const AVAILABLE_NODE_TYPES = [
  { type: "ocr", name: "Dual OCR Engine", icon: FileSearch, desc: "Tesseract + CV Preprocessing" },
  { type: "bates", name: "Bates Stamp", icon: Layers, desc: "Legal sequential numbering" },
  { type: "redact", name: "Deep Redact", icon: Lock, desc: "PII & font glyph scrubbing" },
  { type: "watermark", name: "Watermark", icon: Sparkles, desc: "Custom confidentiality stamp" },
  { type: "encrypt", name: "AES-256 Lock", icon: Lock, desc: "Cryptographic password lock" },
];

export const PipelineCanvas: React.FC = () => {
  const [nodes, setNodes] = useState<NodeItem[]>([
    { id: "1", type: "ocr", name: "Dual OCR Engine", status: "PENDING", config: { lang: "eng" } },
    { id: "2", type: "bates", name: "Bates Stamp", status: "PENDING", config: { prefix: "CASE-2026-" } },
    { id: "3", type: "redact", name: "Deep Redact", status: "PENDING", config: { scrubPII: true } },
    { id: "4", type: "encrypt", name: "AES-256 Lock", status: "PENDING", config: { key: "AES-256" } },
  ]);
  const [isRunning, setIsRunning] = useState(false);

  const addNode = (typeObj: (typeof AVAILABLE_NODE_TYPES)[0]) => {
    const newNode: NodeItem = {
      id: String(Date.now()),
      type: typeObj.type,
      name: typeObj.name,
      status: "PENDING",
      config: {},
    };
    setNodes((prev) => [...prev, newNode]);
  };

  const removeNode = (id: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== id));
  };

  const runPipeline = async () => {
    setIsRunning(true);
    for (let i = 0; i < nodes.length; i++) {
      // Mark as RUNNING
      setNodes((prev) =>
        prev.map((n, idx) => (idx === i ? { ...n, status: "RUNNING" } : n))
      );
      await new Promise((r) => setTimeout(r, 1200));
      // Mark as COMPLETED
      setNodes((prev) =>
        prev.map((n, idx) => (idx === i ? { ...n, status: "COMPLETED" } : n))
      );
    }
    setIsRunning(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Action Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Visual Workflow Pipeline DAG</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Chain and execute zero-trust document transformations in an automated directed graph.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={runPipeline}
            disabled={isRunning || nodes.length === 0}
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-primary to-accent px-5 py-2.5 text-sm font-semibold text-white shadow-md hover:opacity-95 disabled:opacity-50 transition-all"
          >
            <Play className="h-4 w-4 fill-white" />
            <span>{isRunning ? "Executing Pipeline..." : "Run Pipeline"}</span>
          </button>
        </div>
      </div>

      {/* Available Node Catalog Drawer */}
      <div className="rounded-xl border border-surface-border bg-surface p-4 shadow-sm">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
          Add Transformation Nodes
        </span>
        <div className="mt-3 flex flex-wrap gap-2">
          {AVAILABLE_NODE_TYPES.map((nt) => {
            const Icon = nt.icon;
            return (
              <button
                key={nt.type}
                onClick={() => addNode(nt)}
                className="flex items-center gap-2 rounded-lg border border-surface-border bg-surface-dark px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-200 hover:border-blue-500 dark:hover:border-accent hover:text-blue-600 dark:hover:text-accent shadow-sm transition-all"
              >
                <Plus className="h-3.5 w-3.5" />
                <Icon className="h-3.5 w-3.5 text-blue-600 dark:text-accent" />
                <span>{nt.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Interactive Node DAG Flow Canvas */}
      <div className="rounded-xl border border-surface-border bg-slate-100 dark:bg-[#0A0F1D] p-8 shadow-inner overflow-x-auto">
        <div className="flex items-center gap-4 min-w-[700px]">
          {nodes.map((node, index) => (
            <React.Fragment key={node.id}>
              <div
                className={`relative flex flex-col justify-between w-64 rounded-xl border p-4 shadow-sm transition-all duration-300 ${
                  node.status === "RUNNING"
                    ? "border-blue-500 dark:border-accent bg-blue-50/80 dark:bg-accent/10 shadow-md animate-pulse scale-105"
                    : node.status === "COMPLETED"
                    ? "border-success/60 bg-green-50 dark:bg-success/5"
                    : "border-surface-border bg-white dark:bg-surface/80"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="rounded bg-slate-200 dark:bg-surface-border px-2 py-0.5 text-[10px] font-mono text-gray-600 dark:text-gray-400">
                    Step {index + 1}
                  </span>
                  <button
                    onClick={() => removeNode(node.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="my-3">
                  <h4 className="text-sm font-bold text-gray-900 dark:text-white">{node.name}</h4>
                  <p className="text-[11px] text-gray-500 dark:text-gray-400 font-mono mt-0.5">Type: {node.type}</p>
                </div>

                {/* Status Indicator */}
                <div className="flex items-center justify-between pt-2 border-t border-surface-border/50 text-xs">
                  <span className="text-gray-500 dark:text-gray-400">Status:</span>
                  <span
                    className={`font-mono font-bold text-[11px] flex items-center gap-1 ${
                      node.status === "COMPLETED"
                        ? "text-success"
                        : node.status === "RUNNING"
                        ? "text-blue-600 dark:text-accent"
                        : "text-gray-500 dark:text-gray-400"
                    }`}
                  >
                    {node.status === "COMPLETED" && <CheckCircle2 className="h-3.5 w-3.5" />}
                    {node.status === "RUNNING" && <Clock className="h-3.5 w-3.5 animate-spin" />}
                    {node.status}
                  </span>
                </div>
              </div>

              {/* Edge Connection Arrow */}
              {index < nodes.length - 1 && (
                <div className="text-gray-400 dark:text-gray-600">
                  <ArrowRight className="h-5 w-5 animate-pulse" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
