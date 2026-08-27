import { requireCreatorForSlug } from "../actions";
import { WorkspaceTopbar } from "./WorkspaceTopbar";

export const dynamic = "force-dynamic";

export default async function CreatorWorkspaceLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ creatorSlug: string }>;
}) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);

  return (
    <>
      <WorkspaceTopbar creatorSlug={creator.slug} creatorName={creator.name} />
      <div className="ch-container">{children}</div>
    </>
  );
}
