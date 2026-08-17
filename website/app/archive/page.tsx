import { ArchiveBrowser } from "../../components/ArchiveBrowser";
import { getArchiveIndex } from "../../lib/archive";

export const metadata = {
  title: "Beat the Model Archive",
  description: "Browse historical Beat the Model weekly slates and model results.",
};

export default function ArchivePage() {
  const index = getArchiveIndex();
  return (
    <>
      <section className="page-hero compact-hero btm-page-hero">
        <span className="eyebrow">THE RECEIPTS</span>
        <h1>Every official slate stays public.</h1>
        <p>Go back week by week to see which games made the Official 15, where each team was ranked, what The Model picked, and how it finished.</p>
      </section>
      <ArchiveBrowser index={index} />
    </>
  );
}
