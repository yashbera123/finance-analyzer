import { Inter } from "next/font/google";
import "./globals.css";
import SessionProvider from "@/components/SessionProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata = {
  title: "Finance Analyzer — AI-Powered Personal Finance",
  description:
    "Upload your bank statements and get instant AI-powered spending analysis, behavioral profiling, and actionable financial recommendations.",
  keywords: ["finance", "analyzer", "AI", "spending", "budget", "personal finance"],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
        {/* Background glow effect */}
        <div
          className="pointer-events-none fixed inset-0 z-0"
          style={{ background: "var(--gradient-glow)" }}
          aria-hidden
        />

        {/* Main content */}
        <SessionProvider>
          <main className="relative z-10">{children}</main>
        </SessionProvider>
      </body>
    </html>
  );
}
