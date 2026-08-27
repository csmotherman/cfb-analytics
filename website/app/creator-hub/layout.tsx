import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Creator Hub",
  description: "Private collaboration workspace.",
  robots: { index: false, follow: false },
};

export default function CreatorHubLayout({ children }: { children: React.ReactNode }) {
  return <div className="ch-shell">{children}</div>;
}
