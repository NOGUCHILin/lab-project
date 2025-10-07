/**
 * 🚀 NEW SIMPLIFIED Root Layout
 * No complex service providers - just pure HTML layout
 */

import type { Metadata } from "next";
import SystemBar from "@/components/system/SystemBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "統合ダッシュボード v2.0",
  description: "NixOS統合ダッシュボード - シンプル・高速・直接接続",
  keywords: ["NixOS", "Dashboard", "Services", "Simple"],
  authors: [{ name: "Dashboard Team" }],
  robots: "noindex, nofollow", // Private dashboard
};

// Move viewport to separate export as required by Next.js 15
export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="dark">
      <body className="antialiased bg-gray-900 text-white">
        {/* Simple, clean layout with no complex providers */}
        {children}
        {/* Realtime system metrics bar */}
        <SystemBar />

        {/* Optional: Add error boundary or simple analytics in the future */}
      </body>
    </html>
  );
}
