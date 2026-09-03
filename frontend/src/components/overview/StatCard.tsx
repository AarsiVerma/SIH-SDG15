"use client";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  trend?: string;
  color?: "green" | "yellow" | "red" | "blue";
}

export default function StatCard({ label, value, icon, trend, color = "blue" }: StatCardProps) {
  const colors = {
    green: "bg-green-900/30 border-green-700 text-green-300",
    yellow: "bg-yellow-900/30 border-yellow-700 text-yellow-300",
    red: "bg-red-900/30 border-red-700 text-red-300",
    blue: "bg-blue-900/30 border-blue-700 text-blue-300",
  };

  return (
    <div className={`rounded-xl border p-5 ${colors[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-100">{value}</p>
          {trend && <p className="text-sm text-gray-400 mt-1">{trend}</p>}
        </div>
        <span className="text-4xl">{icon}</span>
      </div>
    </div>
  );
}