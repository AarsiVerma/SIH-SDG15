"use client";

import { ACTIVITY_STATS } from "@/types/dashboard";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

export function ActivityCharts() {
  const chartData = ACTIVITY_STATS.map((item) => ({
    name: item.name,
    value: item.count,
    color: item.color,
  }));

  const HOURLY_BARS = [
    { hour: "00:00", val: 5 },
    { hour: "02:00", val: 8 },
    { hour: "04:00", val: 15 },
    { hour: "06:00", val: 32 },
    { hour: "08:00", val: 48 },
    { hour: "10:00", val: 62 },
    { hour: "12:00", val: 40 },
    { hour: "14:00", val: 35 },
    { hour: "16:00", val: 28 },
    { hour: "18:00", val: 18 },
    { hour: "20:00", val: 10 },
    { hour: "22:00", val: 6 },
  ];

  return (
    <div className="flex h-full flex-col rounded-2xl border border-[#E2E0D8] bg-white p-6 shadow-2xs dark:border-[#262626] dark:bg-[#0a0a0a]">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="font-serif text-lg font-normal text-[#181918] dark:text-white">
            Activity Overview
          </h3>
          <p className="text-xs text-[#6B7260] dark:text-gray-400">
            Event breakdown & hourly trend
          </p>
        </div>
      </div>

      <div className="flex flex-col items-center justify-between gap-4 sm:flex-row my-2">
        <div className="relative h-32 w-32 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={38}
                outerRadius={56}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="font-serif text-base font-semibold text-[#181918] dark:text-white">
              128
            </span>
            <span className="text-[9px] text-[#6B7260] dark:text-gray-400">
              Events
            </span>
          </div>
        </div>

        <div className="w-full flex-1 space-y-1 text-xs">
          {ACTIVITY_STATS.map((stat) => (
            <div key={stat.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: stat.color }}
                />
                <span className="text-[11px] text-[#6B7260] dark:text-gray-400">
                  {stat.name}
                </span>
              </div>
              <span className="font-medium text-[#181918] text-[11px] dark:text-white">
                {stat.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-[#E2E0D8] dark:border-[#262626]">
        <p className="text-[10px] text-[#6B7260] dark:text-gray-400 mb-2">
          Hourly Distribution (24h)
        </p>
        <div className="flex h-16 items-end gap-1 px-1">
          {HOURLY_BARS.map((bar) => {
            const heightPercent = (bar.val / 62) * 100;
            return (
              <div
                key={bar.hour}
                className="group relative flex flex-1 flex-col items-center h-full justify-end"
              >
                <div
                  style={{ height: `${heightPercent}%` }}
                  className="w-full rounded-xs bg-[#C08A3E]/70 group-hover:bg-[#C08A3E] transition-all"
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
