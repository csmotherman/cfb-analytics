import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import "./archive.css";
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
    default: "CFB Model — College Football Predictions Explained",
    template: "%s | CFB Model",
  },
  description: "Weekly college football predictions with projected scores, win probabilities, and three clear reasons behind every pick.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetBrainsMono.variable}`}>
        <Nav />
        <main className="shell site-main">{children}</main>
        <footer className="site-footer">
          <div className="shell footer-inner">
            <strong>CFB MODEL</strong>
            <span>Predictions are model estimates, not guarantees.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
