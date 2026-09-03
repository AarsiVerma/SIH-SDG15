"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/command", label: "Overview", icon: "📊" },
  { href: "/command/map", label: "Map", icon: "🗺️" },
  { href: "/command/incidents", label: "Incidents", icon: "🚨" },
  { href: "/command/cameras", label: "Cameras", icon: "📹" },
  { href: "/command/wildlife", label: "Wildlife", icon: "🦌" },
  { href: "/command/fire", label: "Fire", icon: "🔥" },
  { href: "/command/rangers", label: "Rangers", icon: "👮" },
  { href: "/command/health", label: "Camera Health", icon: "📡" },
  { href: "/command/analytics", label: "Analytics", icon: "📈" },
  { href: "/command/evidence", label: "Evidence", icon: "📁" },
];

export default function CommandShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-forest-900 text-gray-100">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 bg-forest-800 border-r border-forest-700 transition-all duration-300 ${
          sidebarOpen ? "w-64" : "w-20"
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-forest-700">
            {sidebarOpen && (
              <span className="font-bold text-lg text-forest-300">VANRAKSHA AI</span>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded hover:bg-forest-700"
              aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
            >
              {sidebarOpen ? "◀" : "▶"}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-2 space-y-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? "bg-forest-700 text-forest-100"
                      : "text-gray-300 hover:bg-forest-700 hover:text-forest-100"
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  {sidebarOpen && <span className="font-medium">{item.label}</span>}
                </Link>
              );
            })}
          </nav>

          {/* Verification banner */}
          {sidebarOpen && (
            <div className="p-3 border-t border-forest-700 bg-forest-900/50">
              <p className="text-xs text-gray-400 text-center">
                ⚠ AI outputs require human verification
              </p>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main
        className={`flex-1 overflow-auto transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-20"
        }`}
      >
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}