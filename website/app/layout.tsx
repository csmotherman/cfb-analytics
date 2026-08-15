import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "../components/Nav";

export const metadata: Metadata = {
  title: "CFB Analytics Pilot",
  description: "Fan-first college football analytics pilot",
};

export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en"><body><Nav/><main className="shell">{children}</main></body></html>;
}
