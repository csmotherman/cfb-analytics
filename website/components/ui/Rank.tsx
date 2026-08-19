export function NationalRank({ rank }: { rank?: number | null }) { return <span className="data-label">{rank ? `#${rank} NATIONALLY` : "NOT RANKED YET"}</span>; }
export function ConferenceRank({ rank }: { rank?: number | null }) { return <span className="data-label">{rank ? `#${rank} BIG TEN` : "NOT RANKED YET"}</span>; }
