import { ArchiveBrowser } from "../../components/ArchiveBrowser";
import { getArchiveIndex } from "../../lib/archive";

export const metadata = {
  title: "College Football Prediction Archive",
  description: "Browse college football week by week from 2014 through 2025.",
};

export default function ArchivePage() {
  const index = getArchiveIndex();
  return (
    <>
      <section className="page-hero compact-hero">
        <span className="eyebrow">2014–2025</span>
        <h1>Prediction archive.</h1>
        <p>Pick a season and a week. The archive keeps the historical slate and only labels a model prediction when the stored data supports that claim.</p>
      </section>
      <ArchiveBrowser index={index} />
    </>
  );
}
