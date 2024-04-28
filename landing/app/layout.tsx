import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MailForge — Bulk personalized email, previewed before it sends",
  description:
    "A Python CLI for sending personalized bulk email from a CSV + Jinja2 template, with an HTML dry-run preview and a built-in send rate limiter.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#08090c] text-[#e7e9ea]">
        {children}
      </body>
    </html>
  );
}
