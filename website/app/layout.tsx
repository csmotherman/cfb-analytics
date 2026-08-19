import type { Metadata, Viewport } from "next";
import "./globals.css";
import "../styles/importance.css";
import { SiteNav } from "../components/SiteNav";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: { default: "SOAR Analytics | Michigan Football Focus", template: "%s | SOAR Analytics" },
  description: "SOAR Analytics maps Michigan football strength, identity, roster intelligence, recruiting, and history for fans.",
  openGraph: { title: "SOAR Analytics | Michigan Football Focus", description: "The 2026 Michigan season, mapped through strength, identity, and trajectory.", images: ["/og.png"] },
  twitter: { card: "summary_large_image", title: "SOAR Analytics | Michigan Football Focus", description: "The 2026 Michigan season, mapped through strength, identity, and trajectory.", images: ["/og.png"] },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#061324" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" data-scroll-behavior="smooth"><body><SiteNav /><main>{children}</main><footer><div className="wrap footer-inner"><div><b>SOAR ANALYTICS</b><span>Michigan Football Focus · Michigan football, understood.</span></div><nav aria-label="Footer"><a href="/articles">Articles</a><a href="/recruiting/portal">Transfers</a><a href="/methodology">Methodology</a></nav></div></footer></body></html>;
}
