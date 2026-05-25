import type { Metadata } from "next";
import "./globals.css";
import { MathJax } from "@/components/MathJax";
import { SearchBar } from "@/components/SearchBar";
import Link from "next/link";

export const metadata: Metadata = {
  title: "IB Revision Bank",
  description:
    "Curated, merged question bank for IB Mathematics (AA & AI) and Physics, grouped by syllabus topic.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <Link href="/" className="brand">IB Revision Bank</Link>
          <div className="topbar-tools">
            <SearchBar />
            <Link href="/about/">About</Link>
          </div>
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
