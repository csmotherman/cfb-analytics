import Link from "next/link";
import { supportedSeasons } from "../../lib/michigan/seasons";
export function SeasonSelector({ selected }: { selected?: number }) {
  return <nav className="season-selector" aria-label="Select season">{supportedSeasons.map((season) => <Link className={selected === season ? "active" : ""} href={`/history/${season}`} key={season}>{season}</Link>)}</nav>;
}
