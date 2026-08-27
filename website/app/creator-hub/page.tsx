import type { Metadata } from "next";
import Link from "next/link";
import { hasCreatorHubAccess, isCreatorHubConfigured } from "../../lib/creator-hub-auth";
import { lockCreatorHub, unlockCreatorHub } from "./actions";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Creator Hub",
  description: "Private Michigan Football Focus creator workspace.",
  robots: { index: false, follow: false, nocache: true },
};

type HubCard = {
  eyebrow: string;
  title: string;
  description: string;
  href: string;
  action: string;
};

const hubCards: HubCard[] = [
  {
    eyebrow: "2026 SEASON",
    title: "Season Outlook",
    description: "Start with the current Michigan projection, schedule context, and the season-level case before recording a preview.",
    href: "/2026-projection",
    action: "Open outlook",
  },
  {
    eyebrow: "BASELINE",
    title: "2025 Michigan",
    description: "Use last season as the factual baseline: what worked, what failed, and what the returning roster is building from.",
    href: "/analytics?year=2025",
    action: "Open baseline",
  },
  {
    eyebrow: "OFFENSE",
    title: "Offensive Evidence",
    description: "Drives, efficiency, explosiveness, run/pass splits, and the numbers behind Michigan's offensive identity.",
    href: "/analytics/offense?year=2025",
    action: "Open offense",
  },
  {
    eyebrow: "DEFENSE",
    title: "Defensive Evidence",
    description: "The cleanest place to pressure-test claims about run defense, scoring prevention, explosiveness, and down-to-down consistency.",
    href: "/analytics/defense?year=2025",
    action: "Open defense",
  },
  {
    eyebrow: "COACHING",
    title: "Staff Tendencies",
    description: "Use coaching and play-calling context to connect scheme changes to what Michigan may look like on Saturdays.",
    href: "/analytics/staff?year=2025",
    action: "Open staff data",
  },
  {
    eyebrow: "ROSTER",
    title: "Player Profiles",
    description: "Move from the team-level argument into the players who actually have to make it happen.",
    href: "/players",
    action: "Open players",
  },
  {
    eyebrow: "MODEL",
    title: "Predictions",
    description: "Use model outputs as evidence, not certainty. This is the place to compare the numbers with your own football read.",
    href: "/predictions",
    action: "Open predictions",
  },
  {
    eyebrow: "EDITORIAL",
    title: "Story Angles",
    description: "Jump into published Michigan Football Focus stories when you want context, framing, or a supporting argument for a segment.",
    href: "/articles",
    action: "Open articles",
  },
];

const previewQuestions = [
  "Is Michigan being judged like the 2025 team instead of the 2026 team?",
  "How much does returning offensive experience change the floor?",
  "What does the new offensive staff actually change for Bryce Underwood?",
  "Can Michigan create more explosive passing opportunities without abandoning the run game?",
  "Where is the defense most vulnerable while new starters settle in?",
  "Which games on the schedule are true matchup problems rather than just big-name opponents?",
];

function CreatorHubGate({ error }: { error?: string }) {
  const configured = isCreatorHubConfigured();
  const message = error === "invalid"
    ? "That password did not match. Try again."
    : error === "setup"
      ? "Creator access is not configured yet."
      : null;

  return <div className="creator-hub creator-hub-gate">
    <section className="creator-gate-panel" aria-labelledby="creator-hub-title">
      <div className="creator-gate-mark" aria-hidden="true"><span>M</span></div>
      <span className="creator-hub-kicker">PRIVATE CREATOR ACCESS</span>
      <h1 id="creator-hub-title">CREATOR<br/><b>HUB</b></h1>
      <p>Broadcast-ready Michigan Football Focus research, visuals, and source material for approved collaborators.</p>

      {configured ? <form action={unlockCreatorHub} className="creator-gate-form">
        <label htmlFor="creator-hub-password">PASSWORD</label>
        <div className="creator-password-row">
          <input id="creator-hub-password" name="password" type="password" autoComplete="current-password" required autoFocus aria-describedby={message ? "creator-hub-error" : undefined}/>
          <button type="submit">ENTER HUB <span aria-hidden="true">→</span></button>
        </div>
        {message && <p id="creator-hub-error" className="creator-gate-error" role="alert">{message}</p>}
      </form> : <div className="creator-gate-unavailable">
        <strong>ACCESS NOT CONFIGURED</strong>
        <p>The private workspace will open once its server-side password is configured.</p>
      </div>}

      <small>Private workspace · Not indexed · Access expires automatically</small>
    </section>
  </div>;
}

export default async function CreatorHubPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const params = await searchParams;
  const authorized = await hasCreatorHubAccess();

  if (!authorized) return <CreatorHubGate error={params.error}/>;

  return <div className="creator-hub creator-hub-workspace">
    <header className="creator-hub-hero">
      <div className="creator-hub-hero-grid" aria-hidden="true"/>
      <div className="creator-hub-shell creator-hub-hero-inner">
        <div>
          <span className="creator-hub-kicker">MICHIGAN FOOTBALL FOCUS · PRIVATE</span>
          <h1>CREATOR<br/><b>HUB</b></h1>
          <p>Research faster. Find the argument. Put the evidence on screen. Built as a private prep room for Darren Talks Ball.</p>
        </div>
        <div className="creator-hub-status">
          <span>CREATOR ACCESS</span>
          <strong>AUTHORIZED</strong>
          <p>Use anything in this workspace as a starting point for video research. Public-facing data pages remain the source of truth.</p>
          <form action={lockCreatorHub}><button type="submit">LOCK HUB</button></form>
        </div>
      </div>
    </header>

    <div className="creator-hub-shell creator-hub-content">
      <section className="creator-feature" aria-labelledby="creator-feature-title">
        <div className="creator-feature-heading">
          <div><span>FEATURED PREP</span><h2 id="creator-feature-title">2026 MICHIGAN PREVIEW</h2></div>
          <Link href="/2026-projection">OPEN FULL OUTLOOK <span aria-hidden="true">→</span></Link>
        </div>
        <div className="creator-feature-body">
          <div className="creator-feature-copy">
            <span>THE CORE QUESTION</span>
            <h3>WHAT WOULD HAVE TO BE TRUE FOR MICHIGAN TO BE MUCH BETTER THAN THE CONSENSUS?</h3>
            <p>Use the hub to attack that question from multiple angles instead of relying on one preseason ranking or one narrative.</p>
          </div>
          <ol className="creator-question-list">
            {previewQuestions.map((question, index) => <li key={question}><span>{String(index + 1).padStart(2, "0")}</span><p>{question}</p></li>)}
          </ol>
        </div>
      </section>

      <section className="creator-library" aria-labelledby="creator-library-title">
        <div className="creator-section-heading">
          <div><span>CREATOR LIBRARY</span><h2 id="creator-library-title">FIND THE EVIDENCE</h2></div>
          <p>Each route below is a source surface. Pull the strongest visual or number that actually supports the segment you are making.</p>
        </div>
        <div className="creator-card-grid">
          {hubCards.map(card => <Link className="creator-hub-card" href={card.href} key={card.title}>
            <span>{card.eyebrow}</span>
            <h3>{card.title}</h3>
            <p>{card.description}</p>
            <b>{card.action} <span aria-hidden="true">→</span></b>
          </Link>)}
        </div>
      </section>

      <section className="creator-workflow" aria-labelledby="creator-workflow-title">
        <div><span>HOW TO USE IT</span><h2 id="creator-workflow-title">ARGUMENT → EVIDENCE → VISUAL</h2></div>
        <div className="creator-workflow-steps">
          <article><strong>01</strong><h3>Start with the claim</h3><p>Decide what the segment is actually arguing before opening twenty charts.</p></article>
          <article><strong>02</strong><h3>Pressure-test it</h3><p>Find the strongest supporting and contradicting evidence. If the numbers do not support the claim, change the claim.</p></article>
          <article><strong>03</strong><h3>Show one thing</h3><p>Use the cleanest visual that makes the point instantly on screen instead of burying the audience in metrics.</p></article>
        </div>
      </section>
    </div>
  </div>;
}
