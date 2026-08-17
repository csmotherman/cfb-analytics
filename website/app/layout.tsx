import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import "./archive.css";
import "./beat-the-model.css";
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
    default: "Beat the Model — College Football Picking Game",
    template: "%s | Beat the Model",
  },
  description: "Pick the winners of the 15 biggest college football games each week and see if you can Beat the Model.",
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
            <span>Pick winners. Compete with The Model. Keep the receipts.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
