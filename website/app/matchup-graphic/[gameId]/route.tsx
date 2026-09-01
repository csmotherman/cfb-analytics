import { ImageResponse } from "next/og";
import { buildMatchupGraphicData } from "../../../lib/matchup-graphic/build-matchup";
import { MatchupGraphic } from "../../../lib/matchup-graphic/presentation";

// nodejs runtime (not edge): buildMatchupGraphicData reads published JSON
// off disk via lib/server-data.ts's readJson, which uses node:fs and has
// no edge-runtime equivalent. This is also Next's own recommended runtime
// for ImageResponse now (the edge runtime is deprecated).
const GRAPHIC_WIDTH = 1600;
const GRAPHIC_HEIGHT = 900;

async function loadGoogleFont(family: string, weight: number): Promise<ArrayBuffer | null> {
  try {
    const css = await (await fetch(`https://fonts.googleapis.com/css2?family=${encodeURIComponent(family)}:wght@${weight}`)).text();
    const match = css.match(/src: url\(([^)]+)\) format\('(?:opentype|truetype)'\)/);
    if (!match) return null;
    const res = await fetch(match[1]);
    return res.status === 200 ? await res.arrayBuffer() : null;
  } catch {
    return null;
  }
}

export async function GET(_request: Request, { params }: { params: Promise<{ gameId: string }> }) {
  const { gameId } = await params;
  const data = buildMatchupGraphicData(gameId);
  if (!data) {
    return new Response(`No matchup graphic data published for game ${gameId}`, { status: 404 });
  }

  const [barlowBold, interRegular, interSemibold, interBold] = await Promise.all([
    loadGoogleFont("Barlow Condensed", 700),
    loadGoogleFont("Inter", 400),
    loadGoogleFont("Inter", 600),
    loadGoogleFont("Inter", 700),
  ]);
  const fonts = [
    barlowBold && { name: "Barlow Condensed", data: barlowBold, weight: 700 as const, style: "normal" as const },
    interRegular && { name: "Inter", data: interRegular, weight: 400 as const, style: "normal" as const },
    interSemibold && { name: "Inter", data: interSemibold, weight: 600 as const, style: "normal" as const },
    interBold && { name: "Inter", data: interBold, weight: 700 as const, style: "normal" as const },
  ].filter((f): f is NonNullable<typeof f> => Boolean(f));

  return new ImageResponse(<MatchupGraphic data={data} />, { width: GRAPHIC_WIDTH, height: GRAPHIC_HEIGHT, fonts });
}
