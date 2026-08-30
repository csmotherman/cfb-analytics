import Link from "next/link";
import { notFound } from "next/navigation";
import { requireCreatorForSlug } from "../../../actions";
import { getAllScoutingReports, findScoutingReport } from "../../../../../lib/creator-hub/scouting";
import { TeamLogo } from "../../../../../components/ui/TeamLogo";

export const dynamic = "force-dynamic";

function ScoutingList({ creatorSlug }: { creatorSlug: string }) {
  const reports = getAllScoutingReports();

  return (
    <>
      <div className="ch-page-head">
        <div><h1>Scouting</h1><p>Numbers-first opponent outlooks, ready to read straight into a video.</p></div>
      </div>

      {reports.length === 0 ? (
        <div className="ch-empty">No scouting reports published yet.</div>
      ) : (
        <div className="ch-video-list">
          {reports.map((r) => (
            <Link key={r.slug} href={`/creator-hub/${creatorSlug}/scouting/${r.slug}`} className="ch-card ch-card-pad ch-game-row">
              <div className="ch-game-row-score">
                {r.opponentTeamId != null && <TeamLogo teamId={r.opponentTeamId} name={r.opponent} size={64} className="ch-game-row-logo" />}
              </div>
              <div className="ch-game-row-body">
                <div className="meta">{r.season} · {r.matchupContext}</div>
                <div className="headline">{r.opponent}</div>
                <div className="meta">{r.record}</div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}

export default async function ScoutingPage({
  params,
}: {
  params: Promise<{ creatorSlug: string; report: string }>;
}) {
  const { creatorSlug, report: reportSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);

  if (reportSlug === "all") return <ScoutingList creatorSlug={creator.slug} />;

  const report = findScoutingReport(reportSlug);
  if (!report) notFound();

  return (
    <>
      <Link href={`/creator-hub/${creator.slug}/scouting`} className="ch-btn ch-btn-ghost ch-btn-sm" style={{ marginBottom: 18, display: "inline-flex" }}>&larr; Scouting</Link>

      <div className="ch-page-head">
        <div>
          <h1 style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {report.opponentTeamId != null && <TeamLogo teamId={report.opponentTeamId} name={report.opponent} size={64} />}
            {report.opponent} — {report.season} Outlook
          </h1>
          <p>{report.matchupContext} · {report.record}</p>
        </div>
      </div>

      <section className="ch-section">
        <div className="ch-card ch-card-pad">
          <ul className="ch-talking-points">
            {report.overview.map((line, i) => <li key={i}>{line}</li>)}
          </ul>
        </div>
      </section>

      {report.sections.map((section) => (
        <section key={section.id} id={section.id} className="ch-section">
          <div className="ch-section-head"><h2>{section.title}</h2></div>

          {section.intro?.map((p, i) => (
            <p key={i} style={{ fontSize: 13.5, color: "var(--ch-text-dim)", lineHeight: 1.6, margin: "0 0 12px" }}>{p}</p>
          ))}

          {section.tables?.map((table, i) => (
            <div key={i} style={{ marginBottom: 16 }}>
              {table.caption && (
                <div style={{ fontSize: 11.5, fontWeight: 700, color: "var(--ch-text-faint)", textTransform: "uppercase", letterSpacing: ".04em", marginBottom: 6 }}>
                  {table.caption}
                </div>
              )}
              <div className="ch-insight-table-wrap">
                <table className="ch-insight-table">
                  <thead>
                    <tr>{table.columns.map((c, ci) => <th key={ci}>{c}</th>)}</tr>
                  </thead>
                  <tbody>
                    {table.rows.map((row, ri) => (
                      <tr key={ri}>
                        {row.map((cell, ci) => (
                          <td key={ci} className={ci > 0 ? "numeric" : undefined}>{cell || "—"}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}

          {section.bullets && (
            <ul className="ch-talking-points">
              {section.bullets.map((b, i) => <li key={i}>{b}</li>)}
            </ul>
          )}
        </section>
      ))}

      <section className="ch-section">
        <div className="ch-section-head"><h2>Wording guardrails</h2></div>
        <div className="ch-card ch-card-pad">
          <ul className="ch-talking-points">
            {report.guardrails.map((g, i) => <li key={i}>{g}</li>)}
          </ul>
        </div>
      </section>

      <section className="ch-section">
        <div className="ch-section-head"><h2>Sources</h2></div>
        <div className="ch-card ch-card-pad">
          <ul className="ch-talking-points">
            {report.sources.map((s) => (
              <li key={s.url}><a href={s.url} target="_blank" rel="noreferrer" style={{ color: "var(--ch-navy)" }}>{s.label} &#8599;</a></li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}
