import { redirect } from "next/navigation";
import { getCreators } from "../../lib/creator-hub/db";
import { getSessionCreator } from "../../lib/creator-hub/auth";
import { CreatorPicker } from "./CreatorPicker";

export const dynamic = "force-dynamic";

export default async function CreatorHubEntry({
  searchParams,
}: {
  searchParams: Promise<{ error?: string; creator?: string }>;
}) {
  const existing = await getSessionCreator();
  if (existing) redirect(`/creator-hub/${existing.slug}`);

  const params = await searchParams;
  const creators = await getCreators();

  return (
    <div className="ch-entry">
      <div className="ch-entry-head">
        <span>Creator Hub</span>
        <h1>Private collaboration workspace</h1>
        <p>Select your workspace to continue.</p>
      </div>
      {creators.length === 0 ? (
        <div className="ch-empty">No creators configured yet.</div>
      ) : (
        <CreatorPicker
          creators={creators.map((c) => ({ id: c.id, slug: c.slug, name: c.name }))}
          initialErrorSlug={params.error === "invalid" ? params.creator ?? null : null}
        />
      )}
    </div>
  );
}
