import type { Metadata } from "next";
import { hasCreatorHubAccess, isCreatorHubConfigured } from "../../lib/creator-hub-auth";
import { lockCreatorHub, unlockCreatorHub } from "./actions";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Creator Hub",
  description: "Private Michigan Football Focus creator workspace.",
  robots: { index: false, follow: false, nocache: true },
};

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
      <p>Private Michigan Football Focus workspace for approved collaborators.</p>

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
    <div className="creator-hub-shell creator-hub-empty">
      <div className="creator-hub-empty-head">
        <div>
          <span className="creator-hub-kicker">MICHIGAN FOOTBALL FOCUS · PRIVATE</span>
          <h1>CREATOR HUB</h1>
        </div>
        <form action={lockCreatorHub}><button type="submit">LOCK HUB</button></form>
      </div>
    </div>
  </div>;
}
