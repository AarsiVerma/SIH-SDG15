"use client";

import { useState } from "react";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Header } from "@/components/dashboard/header";
import { KPICards } from "@/components/dashboard/kpi-cards";
import { CameraGrid } from "@/components/dashboard/camera-grid";
import { AIAlerts } from "@/components/dashboard/ai-alerts";
import { MapView } from "@/components/dashboard/map-view";
import { ActivityCharts } from "@/components/dashboard/activity-charts";
import { RecentDetections } from "@/components/dashboard/recent-detections";
import { FooterBar } from "@/components/dashboard/footer-bar";
import { INITIAL_CAMERAS, INITIAL_ALERTS } from "@/types/dashboard";

export default function DashboardPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="min-h-screen bg-[#F4F5F3] text-[#181918] transition-colors duration-300">
        {/* Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isCollapsed={isCollapsed}
        />

        {/* Main Content Workspace */}
        <div
          className={`flex flex-col min-h-screen transition-all duration-300 ${
            isCollapsed ? "pl-20" : "pl-60"
          }`}
        >
          {/* Header */}
          <Header
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            isCollapsed={isCollapsed}
            setIsCollapsed={setIsCollapsed}
          />

          {/* Main Dashboard Workspace */}
          <main className="flex-1 p-6 sm:p-8 space-y-6">
            {/* Top Summary Metrics */}
            <KPICards />

            {/* Middle Grid Row: Live Camera Feeds (8 Cols) & AI Alerts (4 Cols) */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
              <div className="lg:col-span-8">
                <CameraGrid cameras={INITIAL_CAMERAS} />
              </div>

              <div className="lg:col-span-4">
                <AIAlerts alerts={INITIAL_ALERTS} />
              </div>
            </div>

            {/* Bottom Grid Row: Map View (5 Cols), Recent Detections (3 Cols), Activity Overview Charts (4 Cols) */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 min-h-[380px]">
              <div className="lg:col-span-5">
                <MapView />
              </div>

              <div className="lg:col-span-3">
                <RecentDetections />
              </div>

              <div className="lg:col-span-4">
                <ActivityCharts />
              </div>
            </div>

            {/* Footer Bar */}
            <FooterBar />
          </main>
        </div>
      </div>
    </div>
  );
}
