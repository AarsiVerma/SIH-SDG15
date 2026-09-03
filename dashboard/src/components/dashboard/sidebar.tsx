"use client";

import {
  LayoutDashboard,
  Video,
  BellRing,
  Map,
  Footprints,
  ShieldAlert,
  FileText,
  BarChart3,
  HardDrive,
  Settings,
  TreePine,
  RefreshCw,
} from "lucide-react";
import Image from "next/image";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isCollapsed: boolean;
}

export function Sidebar({ activeTab, setActiveTab, isCollapsed }: SidebarProps) {
  const NAV_ITEMS = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "cameras", label: "Live Cameras", icon: Video },
    { id: "alerts", label: "AI Alerts", icon: BellRing, badge: 6 },
    { id: "map", label: "Map View", icon: Map },
    { id: "wildlife", label: "Wildlife", icon: Footprints },
    { id: "incidents", label: "Incidents", icon: ShieldAlert },
    { id: "reports", label: "Reports", icon: FileText },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "devices", label: "Devices", icon: HardDrive },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside
      className={`fixed left-0 top-0 z-40 flex h-screen flex-col justify-between border-r border-[#E2E0D8] bg-[#F4F5F3] text-[#181918] transition-all duration-300 ${
        isCollapsed ? "w-20" : "w-60"
      }`}
    >
      {/* Top Branding & Menu */}
      <div className="p-5">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#181918] text-[#F1EFE8] shadow-2xs">
            <TreePine className="h-4 w-4 stroke-[1.75]" />
          </div>
          {!isCollapsed && (
            <div>
              <span className="font-serif text-base font-semibold tracking-tight text-[#181918]">
                VanRaksha
              </span>
              <p className="text-[10px] tracking-wider text-[#6B7260] uppercase">
                Surveillance
              </p>
            </div>
          )}
        </div>

        <nav className="mt-8 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-xs transition-all ${
                  isActive
                    ? "bg-white text-[#181918] font-semibold border border-[#E2E0D8] shadow-2xs"
                    : "text-[#6B7260] hover:bg-white/60 hover:text-[#181918]"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`h-4 w-4 shrink-0 ${
                      isActive ? "text-[#C08A3E]" : "text-[#6B7260]"
                    }`}
                  />
                  {!isCollapsed && <span>{item.label}</span>}
                </div>
                {!isCollapsed && item.badge && (
                  <span className="rounded-full bg-[#C08A3E]/15 px-2 py-0.5 text-[10px] font-semibold text-[#C08A3E]">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Profile & Status */}
      <div className="p-4 space-y-3">
        {!isCollapsed && (
          <div className="rounded-xl border border-[#E2E0D8] bg-white p-3 text-xs shadow-2xs">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-[#6B7260]">System Status</span>
              <span className="flex items-center gap-1.5 font-medium text-emerald-700">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse" /> Active
              </span>
            </div>

            <div className="mt-3">
              <div className="flex justify-between text-[11px] text-[#6B7260] mb-1">
                <span>Cameras Online</span>
                <span className="font-semibold text-[#181918]">128 / 142</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#F4F5F3]">
                <div className="h-full w-[90%] rounded-full bg-[#C08A3E]" />
              </div>
            </div>

            <div className="flex items-center justify-between text-[10px] text-[#6B7260] pt-2.5 mt-2.5 border-t border-[#E2E0D8]">
              <span>AI Model</span>
              <span className="flex items-center gap-1 text-[10px] font-medium text-[#181918]">
                2 min ago <RefreshCw className="h-2.5 w-2.5 text-[#C08A3E]" />
              </span>
            </div>
          </div>
        )}

        <div className="flex items-center gap-3 rounded-lg border border-[#E2E0D8] bg-white p-2 shadow-2xs">
          <div className="relative h-7 w-7 shrink-0 overflow-hidden rounded-full border border-[#E2E0D8]">
            <Image
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80&auto=format&fit=crop"
              alt="Forest Officer"
              fill
              className="object-cover"
            />
          </div>
          {!isCollapsed && (
            <div className="overflow-hidden text-xs">
              <p className="truncate font-medium text-[#181918]">Forest Officer</p>
              <p className="truncate text-[10px] text-[#6B7260]">Ranthambore</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
