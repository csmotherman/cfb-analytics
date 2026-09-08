import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Don't Jump the Gun — Why Michigan Football Is in a Better Spot Than It Looks";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          position: "relative",
          overflow: "hidden",
          background: "#f3f0e7",
          color: "#00274c",
          fontFamily: "Georgia, serif",
        }}
      >
        <div style={{ position: "absolute", inset: 0, opacity: 0.18, backgroundImage: "radial-gradient(#00274c 0.8px, transparent 0.8px)", backgroundSize: "7px 7px" }} />
        <div style={{ position: "absolute", right: -70, top: -105, fontSize: 360, fontWeight: 900, color: "#ffcb05", opacity: 0.12 }}>M</div>
        <div style={{ position: "absolute", left: 0, bottom: 0, width: "100%", height: 16, display: "flex" }}>
          <div style={{ width: "48%", background: "#00274c" }} />
          <div style={{ width: "52%", background: "#ffcb05" }} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", width: "100%", padding: "46px 62px 44px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontFamily: "Arial, sans-serif", letterSpacing: 7, fontSize: 17, fontWeight: 700 }}>
            <span>MICHIGAN FOOTBALL</span>
            <span>ANALYSIS · CONTEXT · PERSPECTIVE</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", marginTop: 26 }}>
            <div style={{ fontSize: 100, lineHeight: 0.83, letterSpacing: -5, fontWeight: 700 }}>DON'T JUMP</div>
            <div style={{ fontSize: 110, lineHeight: 0.88, letterSpacing: -6, fontWeight: 700, color: "#d9a900" }}>THE GUN</div>
          </div>

          <div style={{ display: "flex", flex: 1, marginTop: 25, gap: 34 }}>
            <div style={{ display: "flex", width: 330, height: 235, borderRadius: 24, background: "#ffcb05", position: "relative", overflow: "hidden", border: "3px solid #00274c" }}>
              <div style={{ position: "absolute", width: 260, height: 260, borderRadius: "50%", left: 38, top: 26, background: "#00274c" }} />
              <div style={{ position: "absolute", width: 250, height: 86, left: 45, top: 24, background: "#ffcb05", transform: "rotate(-12deg)", borderRadius: 44 }} />
              <div style={{ position: "absolute", width: 185, height: 15, left: 135, top: 130, background: "#00274c", transform: "rotate(6deg)" }} />
              <div style={{ position: "absolute", width: 120, height: 12, left: 182, top: 158, background: "#00274c", transform: "rotate(18deg)" }} />
              <div style={{ position: "absolute", right: 16, bottom: 13, fontFamily: "Arial, sans-serif", fontSize: 18, fontWeight: 900, color: "#00274c" }}>WEEK 1</div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", flex: 1, justifyContent: "center" }}>
              <div style={{ fontFamily: "Arial, sans-serif", fontSize: 20, fontWeight: 800, letterSpacing: 4, lineHeight: 1.45 }}>
                ONE GAME DOESN'T DEFINE A SEASON
              </div>
              <div style={{ width: 90, height: 5, background: "#ffcb05", margin: "17px 0" }} />
              <div style={{ fontFamily: "Arial, sans-serif", fontSize: 28, lineHeight: 1.22, fontWeight: 700 }}>
                WHY MICHIGAN FOOTBALL IS IN A BETTER SPOT THAN IT LOOKS
              </div>
              <div style={{ fontFamily: "Arial, sans-serif", fontSize: 16, letterSpacing: 3, marginTop: 18, opacity: 0.78 }}>
                SOAR ANALYTICS · SEPTEMBER 8, 2026
              </div>
            </div>
          </div>
        </div>
      </div>
    ),
    size,
  );
}
