import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import "./archive.css";
import "./beat-the-model.css";
import "./pools.css";
import "./fan-ui.css";
import "./fan-v2.css";
import "./fan-v3.css";
import "./market-ui.css";
import { Nav } from "../components/Nav";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetBrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Beat the Model — College Football Pick Challenge",
    template: "%s | Beat the Model",
  },
  description: "Pick the winners of the biggest college football games each week, reveal The Model's calls, and see who knows college football better.",
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
      <body className={`${inter.variable} ${jetBrainsMono.variable}`}>
        <Nav />
        <main className="shell site-main">{children}</main>
        <footer className="site-footer">
          <div className="shell footer-inner">
            <strong>BEAT THE MODEL</strong>
            <span>Pick first. Reveal The Model. Keep the receipts.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
