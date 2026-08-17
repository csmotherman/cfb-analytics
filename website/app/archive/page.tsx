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
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">ARCHIVE</span>
          <h1>Every week keeps its receipts.</h1>
          <p>Go back to any published slate to see the Official 15, where each team was ranked, what The Model picked, and how the games finished.</p>
        </div>
      </section>

      <ArchiveBrowser index={index} />
    </>
  );
}
