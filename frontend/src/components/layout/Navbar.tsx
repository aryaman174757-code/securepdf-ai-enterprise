"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Lock, Activity, Sparkles, LogOut, User, Sun, Moon } from "lucide-react";
import { useAppStore } from "@/lib/store";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { email, isPro, logout, token, theme, toggleTheme, setTheme } = useAppStore();

  useEffect(() => {
    const savedTheme = (localStorage.getItem("spdf_theme") as "dark" | "light") || "light";
    setTheme(savedTheme);
  }, [setTheme]);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-surface-border bg-surface/90 backdrop-blur-xl transition-colors">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-md text-white">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <Link href="/" className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">SECUREPDF</span>
            <span className="rounded-md bg-blue-50 dark:bg-accent/10 px-2 py-0.5 text-xs font-semibold text-blue-600 dark:text-accent border border-blue-200 dark:border-accent/20">
              AI v3.0
            </span>
          </Link>
        </div>

        {/* Zero-Trust Live Security Indicator */}
        <div className="hidden md:flex items-center gap-2 rounded-full border border-surface-border bg-surface-dark/80 px-4 py-1.5 text-xs text-gray-700 dark:text-gray-300 shadow-sm">
          <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
          <span className="font-medium">Zero-Trust Ephemeral Containment</span>
          <span className="text-gray-400 dark:text-gray-500">•</span>
          <span className="text-blue-600 dark:text-accent font-mono font-bold">AES-256 GCM</span>
        </div>

        {/* User Navigation / Status & Theme Toggle */}
        <div className="flex items-center gap-4">
          {/* Dark / Light Mode Toggle Button */}
          <button
            onClick={toggleTheme}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-surface-border bg-surface text-gray-700 dark:text-gray-300 hover:text-primary dark:hover:text-accent hover:border-primary/40 dark:hover:border-accent shadow-sm transition-all transform hover:scale-105"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
            aria-label="Toggle Theme"
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4 text-amber-400 transition-transform duration-200" />
            ) : (
              <Moon className="h-4 w-4 text-blue-600 transition-transform duration-200" />
            )}
          </button>

          {token ? (
            <div className="flex items-center gap-3">
              {isPro && (
                <span className="rounded-full bg-gradient-to-r from-amber-500 to-orange-500 px-2.5 py-0.5 text-xs font-bold text-black shadow-sm">
                  ENTERPRISE PRO
                </span>
              )}
              <div className="flex items-center gap-2 rounded-lg border border-surface-border bg-surface px-3 py-1.5 text-sm text-gray-800 dark:text-gray-200 shadow-sm">
                <User className="h-4 w-4 text-blue-600 dark:text-accent" />
                <span className="max-w-[120px] truncate">{email || "User"}</span>
              </div>
              <button
                onClick={() => logout()}
                className="rounded-lg p-2 text-gray-500 hover:bg-surface-dark hover:text-gray-900 dark:hover:text-white transition-colors"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                href="/auth/login"
                className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/auth/signup"
                className="rounded-lg bg-gradient-to-r from-primary to-accent px-4 py-2 text-sm font-semibold text-white shadow-sm hover:opacity-95 transition-opacity"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
