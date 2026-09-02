"use client";

// Scales a fixed-design-size child (the matchup graphic, authored at a
// natural 1600px-wide size) to fill the actual browser viewport with no
// page scrolling, on any screen size -- the "wide layout, size of the
// website screen" requirement. Measures the stage's own natural,
// unscaled box (offsetWidth/offsetHeight are unaffected by a CSS
// transform) rather than assuming a hardcoded height, so this keeps
// working correctly if the content's natural height ever changes.
import { useLayoutEffect, useRef, useState } from "react";
import styles from "./fit-to-screen.module.css";

export function FitToScreen({ children }: { children: React.ReactNode }) {
  const stageRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useLayoutEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;

    function fit() {
      if (!stage) return;
      const naturalWidth = stage.offsetWidth;
      const naturalHeight = stage.offsetHeight;
      if (naturalWidth === 0 || naturalHeight === 0) return;
      setScale(Math.min(window.innerWidth / naturalWidth, window.innerHeight / naturalHeight));
    }

    fit();
    window.addEventListener("resize", fit);
    return () => window.removeEventListener("resize", fit);
  }, []);

  return (
    <div className={styles.viewport}>
      <div ref={stageRef} className={styles.stage} style={{ transform: `scale(${scale})` }}>
        {children}
      </div>
    </div>
  );
}
