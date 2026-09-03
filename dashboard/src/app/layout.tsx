import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VanRaksha AI — Real-time Wildlife Surveillance Dashboard",
  description: "AI-powered wildlife monitoring, automated hazard alerts, live camera grid, and spatial GIS tracking.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-emerald-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
