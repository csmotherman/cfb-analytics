import type { Metadata } from "next";
import "../../styles/creator-hub-mobile.css";

export const metadata: Metadata = {
  title: "Creator Hub",
  description: "Private collaboration workspace.",
  robots: { index: false, follow: false },
};

export default function CreatorHubLayout({ children }: { children: React.ReactNode }) {
  return <div className="ch-shell">{children}</div>;
}
