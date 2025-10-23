import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Navigation } from "@/components/navigation";
import "@/lib/error-logger"; // Initialize global error handlers

export const metadata: Metadata = {
  title: "nakamura-misaki 管理画面",
  description: "nakamura-misaki administration dashboard",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="antialiased">
        <Navigation />
        {children}
      </body>
    </html>
  );
}
