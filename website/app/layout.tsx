import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Nav } from "../components/Nav";
import { siteConfig } from "../lib/site-config";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: { default: siteConfig.siteName, template: `%s | ${siteConfig.shortName}` },
  description: siteConfig.tagline,
  openGraph: { title: siteConfig.siteName, description: siteConfig.tagline, images: [{ url: "/og.png", width: 1731, height: 909, alt: siteConfig.siteName }] },
  twitter: { card: "summary_large_image", title: siteConfig.siteName, description: siteConfig.tagline, images: ["/og.png"] },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#050a11" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><Nav /><main className="shell site-main">{children}</main><footer className="site-footer"><div className="shell footer-inner"><strong>{siteConfig.siteName.toUpperCase()}</strong><span>{siteConfig.tagline}</span></div></footer></body></html>;
}
