import type { MetadataRoute } from "next";

const siteUrl=(process.env.NEXT_PUBLIC_SITE_URL||"https://michiganfootballfocus.com").replace(/\/$/,"");

export default function sitemap(): MetadataRoute.Sitemap {
  const routes=[
    {path:"",priority:1,changeFrequency:"daily" as const},
    {path:"/team",priority:.9,changeFrequency:"weekly" as const},
    {path:"/team/roster",priority:.85,changeFrequency:"weekly" as const},
    {path:"/players",priority:.85,changeFrequency:"weekly" as const},
    {path:"/schedule",priority:.9,changeFrequency:"weekly" as const},
    {path:"/analytics",priority:.85,changeFrequency:"weekly" as const},
    {path:"/articles",priority:.9,changeFrequency:"daily" as const},
    {path:"/rankings",priority:.9,changeFrequency:"weekly" as const},
    {path:"/2026-projection",priority:.9,changeFrequency:"weekly" as const},
    {path:"/new-additions",priority:.75,changeFrequency:"weekly" as const},
    {path:"/methodology",priority:.6,changeFrequency:"monthly" as const},
  ];

  return routes.map(route=>({
    url:`${siteUrl}${route.path}`,
    changeFrequency:route.changeFrequency,
    priority:route.priority,
  }));
}
