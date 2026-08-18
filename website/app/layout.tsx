<<<<<<< HEAD
import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "../components/Nav";

export const metadata: Metadata = {
  title: "CFB Analytics Pilot",
  description: "Fan-first college football analytics pilot",
};

export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en"><body><Nav/><main className="shell">{children}</main></body></html>;
=======
import type { Metadata, Viewport } from "next";
import "./globals.css";
import "./michigan.css";
import { Nav } from "../components/Nav";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: {
    default: "Michigan Football Analytics",
    template: "%s | Michigan Football Analytics",
  },
  description: "Michigan football, measured against every FBS team through validated national analytics.",
  openGraph: {
    title: "Michigan Football Analytics",
    description: "Michigan is the focus. The nation is the measuring stick.",
    images: [{ url: "/og.png", width: 1731, height: 909, alt: "Michigan Football Analytics" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Michigan Football Analytics",
    description: "Michigan is the focus. The nation is the measuring stick.",
    images: ["/og.png"],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#070b11",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main className="shell site-main">{children}</main>
        <footer className="site-footer">
          <div className="shell footer-inner">
            <strong>MICHIGAN FOOTBALL ANALYTICS</strong>
            <span>Michigan is the focus. The nation is the measuring stick.</span>
          </div>
        </footer>
      </body>
    </html>
  );
>>>>>>> 28a9c53 (new design)
}
