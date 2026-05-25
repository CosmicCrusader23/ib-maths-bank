"use client";

import Script from "next/script";
import { usePathname } from "next/navigation";
import { useEffect } from "react";

declare global {
  interface Window {
    MathJax?: {
      typesetPromise?: (els?: HTMLElement[]) => Promise<void>;
      typeset?: (els?: HTMLElement[]) => void;
      startup?: { promise?: Promise<void> };
    };
  }
}

/**
 * MathJax 3 (mml-chtml) — pestle questions ship as MathML inside
 * <span class="mjpage"> blocks, so we use the MathML-CHTML bundle.
 */
export function MathJax() {
  const pathname = usePathname();

  useEffect(() => {
    const mj = window.MathJax;
    if (!mj || !mj.typesetPromise) return;
    const run = () => mj.typesetPromise!().catch(() => undefined);
    if (mj.startup?.promise) {
      mj.startup.promise.then(run);
    } else {
      run();
    }
  }, [pathname]);

  return (
    <>
      <Script
        id="mathjax-config"
        strategy="beforeInteractive"
      >{`
        window.MathJax = {
          tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] },
          options: { renderActions: { addMenu: [] } },
        };
      `}</Script>
      <Script
        id="mathjax-src"
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/mml-chtml.js"
        strategy="afterInteractive"
      />
    </>
  );
}
