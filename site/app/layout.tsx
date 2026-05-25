import type { Metadata } from "next";
import "./globals.css";
import { MathJax } from "@/components/MathJax";
import Link from "next/link";

export const metadata: Metadata = {
  title: "IB Maths Bank",
  description:
    "Curated, merged question bank for IB Mathematics (AA & AI, HL & SL), grouped by syllabus topic.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <Link href="/" className="brand">IB Maths Bank</Link>
          <nav>
            <Link href="/">Topics</Link>
            <Link href="/about">About</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          <p>
            Curated from public revision sources. Questions belong to their
            original authors; this site only links to and re-presents what is
            already publicly available.
          </p>
        </footer>
        <MathJax />
      </body>
    </html>
  );
}
