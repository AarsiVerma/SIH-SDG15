"use client";

interface VerificationBannerProps {
  level: "HIGH" | "CRITICAL";
}

export default function VerificationBanner({ level }: VerificationBannerProps) {
  return (
    <div
      className={`p-3 rounded-lg border-l-4 ${
        level === "CRITICAL"
          ? "bg-red-900/30 border-red-600 text-red-200"
          : "bg-yellow-900/30 border-yellow-600 text-yellow-200"
      }`}
      role="alert"
    >
      <div className="flex items-start gap-2">
        <span className="text-lg">{level === "CRITICAL" ? "🚨" : "⚠️"}</span>
        <div>
          <p className="font-medium">
            {level === "CRITICAL" ? "Critical risk" : "High risk"} detected
          </p>
          <p className="text-sm mt-1">
            Ranger verification required. This assessment is based on automated
            analysis and must be confirmed by a qualified officer before any
            operational response.
          </p>
        </div>
      </div>
    </div>
  );
}