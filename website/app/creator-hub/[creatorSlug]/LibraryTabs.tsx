import Link from "next/link";

export function LibraryTabs({ creatorSlug, active }: { creatorSlug: string; active: "research" | "visuals" | "notes" }) {
  const base = `/creator-hub/${creatorSlug}/library`;
  const tabs: [string, "research" | "visuals" | "notes"][] = [
    ["Research", "research"],
    ["Visuals", "visuals"],
    ["Notes", "notes"],
  ];
  return (
    <div className="ch-library-tabs">
      {tabs.map(([label, key]) => (
        <Link key={key} href={`${base}/${key}`} className={key === active ? "active" : ""}>{label}</Link>
      ))}
    </div>
  );
}
