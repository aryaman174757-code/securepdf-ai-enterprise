"use client";

import React, { useState } from "react";
import {
  Shield,
  Activity,
  Users,
  Cpu,
  Database,
  CheckCircle2,
  AlertTriangle,
  History,
  Lock,
  RefreshCw,
} from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";

export default function AdminDashboardPage() {
  const [telemetry, setTelemetry] = useState({
    totalUsers: 1420,
    activeSessions: 38,
    totalDocuments: 8940,
    aiQueries: 24500,
    workerStatus: "HEALTHY",
    activeWorkers: 4,
    queueBacklog: 0,
    memoryMb: 245.8,
    uptimeHours: 184.2,
  });

  const auditLogs = [
    { id: "1", user: "admin@enterprise.corp", action: "DEEP_REDACTION", ip: "192.168.1.45", time: "2 mins ago" },
    { id: "2", user: "ciso@defense.gov", action: "AES256_ENCRYPT", ip: "10.0.4.12", time: "14 mins ago" },
    { id: "3", user: "auditor@deloitte.com", action: "HYBRID_RAG_QUERY", ip: "172.16.0.8", time: "28 mins ago" },
    { id: "4", user: "legal@fortune500.com", action: "BATES_NUMBERING", ip: "192.168.2.100", time: "1 hour ago" },
  ];

  return (
    <div className="flex flex-1 overflow-hidden">
      <Sidebar />

      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-blue-600 dark:text-accent" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Enterprise Administration & Telemetry</h1>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Live worker health, cryptographic key lifecycle, queue latency, and immutable audit trails.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="rounded-full bg-success/10 border border-success/30 px-3 py-1 text-xs font-semibold text-success flex items-center gap-1.5 font-mono">
              <span className="h-2 w-2 rounded-full bg-success animate-ping" />
              {telemetry.workerStatus} ({telemetry.activeWorkers} Workers Active)
            </span>
          </div>
        </div>

        {/* Live Telemetry Widgets */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="glass-panel rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Total Organizations / Users</span>
              <Users className="h-4 w-4 text-blue-600 dark:text-accent" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{telemetry.totalUsers}</div>
          </div>

          <div className="glass-panel rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Active Zero-Trust Sessions</span>
              <Activity className="h-4 w-4 text-success" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{telemetry.activeSessions}</div>
          </div>

          <div className="glass-panel rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Total Ephemeral Transformations</span>
              <Database className="h-4 w-4 text-primary" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{telemetry.totalDocuments}</div>
          </div>

          <div className="glass-panel rounded-xl p-5 shadow-sm">
            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2 text-xs font-medium">
              <span>Worker Node Memory</span>
              <Cpu className="h-4 w-4 text-warning" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white font-mono">{telemetry.memoryMb} MB</div>
          </div>
        </div>

        {/* Audit Log Stream */}
        <div className="glass-panel rounded-2xl overflow-hidden border border-surface-border shadow-sm">
          <div className="border-b border-surface-border bg-surface-dark px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-blue-600 dark:text-accent" />
              <h2 className="text-sm font-bold uppercase tracking-wider text-gray-900 dark:text-white">
                Immutable Enterprise Audit Trail
              </h2>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">SOC 2 / ISO 27001 Compliant</span>
          </div>

          <div className="divide-y divide-surface-border">
            {auditLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between px-6 py-3.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-surface-dark transition-colors"
              >
                <div className="flex items-center gap-4">
                  <span className="rounded bg-blue-50 dark:bg-accent/10 border border-blue-200 dark:border-accent/20 px-2 py-0.5 font-mono text-[10px] text-blue-600 dark:text-accent font-semibold">
                    {log.action}
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-white">{log.user}</span>
                </div>

                <div className="flex items-center gap-6 font-mono text-[11px] text-gray-500 dark:text-gray-400">
                  <span>IP: {log.ip}</span>
                  <span>{log.time}</span>
                  <span className="text-success flex items-center gap-1 font-semibold">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>VERIFIED</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
