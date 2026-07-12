import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Resume Analyzer",
  description:
    "Analyze resume quality, extract technical skills, measure job fit, and receive actionable feedback.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
