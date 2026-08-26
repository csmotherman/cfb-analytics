import type { Metadata, Viewport } from "next";
import "./globals.css";
import "../styles/importance.css";
import "../styles/ux-polish.css";
import "../styles/mockup-home.css";
import "../styles/player-watch-images.css";
import "../styles/pulse-ranking.css";
import "../styles/article-focus.css";
import "../styles/player-profile-focus.css";
import "../styles/player-profile-mobile.css";
import "../styles/player-game-log.css";
import "../styles/team-hub.css";
import "../styles/team-formation-home.css";
import "../styles/team-depth-formats.css";
import "../styles/roster-directory.css";
import "../styles/schedule-home.css";
import "../styles/matchup-logos.css";
import "../styles/more-page.css";
import "../styles/more-drawer.css";
import "../styles/new-additions.css";
import "../styles/game-preview.css";
import "../styles/expansion.css";
import "../styles/preseason-power.css";
import { SiteNav } from "../components/SiteNav";

const SITE_NAME="Michigan Football Focus";
const SITE_URL=(process.env.NEXT_PUBLIC_SITE_URL||"https://michiganfootballfocus.com").replace(/\/$/,"");
const SITE_DESCRIPTION="Michigan Football Focus covers Michigan Wolverines football with news, 2026 projections, rankings, depth charts, player analysis, schedules and advanced analytics.";
const SOCIAL_IMAGE={url:"/og.png",alt:"Michigan Football Focus — Michigan Wolverines football news, projections and analytics"};

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  applicationName: SITE_NAME,
  title: { default: SITE_NAME, template: `%s | ${SITE_NAME}` },
  description: SITE_DESCRIPTION,
  authors: [{name:SITE_NAME,url:SITE_URL}],
  creator: SITE_NAME,
  publisher: SITE_NAME,
  category: "sports",
  robots: {
    index:true,
    follow:true,
    googleBot:{
      index:true,
      follow:true,
      "max-video-preview":-1,
      "max-image-preview":"large",
      "max-snippet":-1,
    },
  },
  openGraph: {
    type:"website",
    locale:"en_US",
    url:"/",
    siteName:SITE_NAME,
    title:SITE_NAME,
    description:SITE_DESCRIPTION,
    images:[SOCIAL_IMAGE],
  },
  twitter: {
    card:"summary_large_image",
    site:"@umfootballfocus",
    creator:"@umfootballfocus",
    title:SITE_NAME,
    description:SITE_DESCRIPTION,
    images:[SOCIAL_IMAGE],
  },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#031426" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" data-scroll-behavior="smooth"><body><SiteNav /><main>{children}</main><footer><div className="wrap footer-inner"><div><b>MICHIGAN FOOTBALL FOCUS</b><span>Michigan football, understood.</span></div><nav aria-label="Footer"><a href="/articles">Articles</a><a href="/new-additions">New Additions</a><a href="/methodology">Methodology</a></nav></div></footer></body></html>;
}
