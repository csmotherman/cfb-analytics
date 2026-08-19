import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { redirect } from "next/navigation";
import { CURRENT_MICHIGAN_SEASON, MICHIGAN_HISTORY_START } from "../../../lib/michigan";

type Props = { params: Promise<{ season: string }> };

function parseSeason(value: string): number | null {
  if (!/^\d{4}$/.test(value)) return null;
  const season = Number(value);
  return season >= MICHIGAN_HISTORY_START && season <= CURRENT_MICHIGAN_SEASON ? season : null;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const season = parseSeason((await params).season);
  if (season === null) return { title: "Season not found" };
  const description = `${season} Michigan football season, measured against the corresponding ${season} FBS universe.`;
  return {
    title: `${season} Michigan Football`, description,
    openGraph: { title: `${season} Michigan Football`, description, images: [] },
    twitter: { title: `${season} Michigan Football`, description, images: [] },
  };
}

export default async function FootballSeasonPage({ params }: Props) {
  const season = parseSeason((await params).season);
  if (season === null) notFound();
  redirect(season === CURRENT_MICHIGAN_SEASON ? "/" : `/history/${season}`);
}
