import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VANRAKSHA AI — Forest Command Centre",
  description: "Detection, correlation, risk assessment, and incident management for forest operations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-forest-900 text-gray-100">{children}</body>
    </html>
  );
}