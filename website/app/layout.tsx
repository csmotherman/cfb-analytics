import type { Metadata, Viewport } from "next";
import "./globals.css";
import "../styles/importance.css";
import "../styles/ux-polish.css";
import "../styles/mockup-home.css";
import "../styles/matchup-logos.css";
import "../styles/more-page.css";
import "../styles/game-preview.css";
import { SiteNav } from "../components/SiteNav";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: { default: "Michigan Football Focus", template: "%s | Michigan Football Focus" },
  description: "Michigan Football Focus maps Michigan football strength, identity, roster intelligence, recruiting, schedule, analytics, and history for fans.",
  openGraph: { title: "Michigan Football Focus", description: "The 2026 Michigan season, mapped through strength, identity, and trajectory.", images: ["/og.png"] },
  twitter: { card: "summary_large_image", title: "Michigan Football Focus", description: "The 2026 Michigan season, mapped through strength, identity, and trajectory.", images: ["/og.png"] },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#031426" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" data-scroll-behavior="smooth"><body><SiteNav /><main>{children}</main><footer><div className="wrap footer-inner"><div><b>MICHIGAN FOOTBALL FOCUS</b><span>Michigan football, understood.</span></div><nav aria-label="Footer"><a href="/articles">Articles</a><a href="/recruiting/portal">Transfers</a><a href="/methodology">Methodology</a></nav></div></footer></body></html>;
}
