import { ArchiveBrowser } from "../../components/ArchiveBrowser";
import { getArchiveIndex } from "../../lib/archive";

export const metadata = {
  title: "College Football Prediction Archive",
  description: "Browse historical college football market lines, model predictions, and weekly results from 2014 through 2025, excluding 2020.",
};

export default function ArchivePage() {
  const index = getArchiveIndex();
  return (
    <>
      <section className="page-hero compact-hero">
        <span className="eyebrow">PREDICTION ARCHIVE</span>
        <h1>Every week. One clean record.</h1>
        <p>Choose a season and week to compare the historical market spread with the model prediction, then check ATS accuracy, winner accuracy, MAE, and recommended-bet results.</p>
      </section>
      <ArchiveBrowser index={index} />
    </>
  );
}
