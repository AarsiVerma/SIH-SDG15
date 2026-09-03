"use client";

import { Menu, Search, Sun, Moon, Bell } from "lucide-react";

interface HeaderProps {
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  isCollapsed: boolean;
  setIsCollapsed: (val: boolean) => void;
}

export function Header({
  darkMode,
  setDarkMode,
  isCollapsed,
  setIsCollapsed,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[#E2E0D8] bg-[#F4F5F3]/90 px-6 backdrop-blur-md transition-colors dark:border-[#262626] dark:bg-black/90">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-200/60 dark:hover:bg-white/10"
        >
          <Menu className="h-4 w-4 text-[#181918] dark:text-white" />
        </button>

        <div>
          <h2 className="font-serif text-lg font-normal tracking-tight text-[#181918] dark:text-white">
            Dashboard
          </h2>
          <p className="text-[11px] text-[#6B7260] dark:text-gray-400">
            Real-time Wildlife Intelligence &bull; Ranthambore Division
          </p>
        </div>
      </div>

      <div className="hidden max-w-md flex-1 px-8 md:block">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search locations, cameras, events..."
            className="w-full rounded-full border border-[#E2E0D8] bg-white px-4 py-1.5 pl-9 text-xs text-[#181918] placeholder-gray-400 focus:border-[#C08A3E] focus:outline-none dark:border-[#262626] dark:bg-[#111111] dark:text-white"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-1.5 rounded-full border border-emerald-600/20 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800 sm:flex dark:border-emerald-500/20 dark:bg-emerald-950 dark:text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse" />
          <span>Live Stream</span>
        </div>

        <button
          onClick={() => setDarkMode(!darkMode)}
          title="Toggle Theme"
          className="flex h-8 w-8 items-center justify-center rounded-full border border-[#E2E0D8] bg-white text-[#181918] transition-colors hover:bg-gray-100 dark:border-[#262626] dark:bg-[#111111] dark:text-white dark:hover:bg-white/10"
        >
          {darkMode ? <Sun className="h-3.5 w-3.5 text-[#C08A3E]" /> : <Moon className="h-3.5 w-3.5 text-gray-700" />}
        </button>

        <button className="relative flex h-8 w-8 items-center justify-center rounded-full border border-[#E2E0D8] bg-white text-[#181918] hover:bg-gray-100 dark:border-[#262626] dark:bg-[#111111] dark:text-white dark:hover:bg-white/10">
          <Bell className="h-3.5 w-3.5" />
          <span className="absolute -right-0.5 -top-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-[#C08A3E] text-[9px] font-bold text-white">
            6
          </span>
        </button>
      </div>
    </header>
  );
}
