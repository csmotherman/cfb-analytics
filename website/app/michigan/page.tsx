import type { Metadata } from "next";
import { MichiganHome } from "../../components/MichiganHome";
import { CURRENT_MICHIGAN_SEASON } from "../../lib/michigan";

export const metadata: Metadata = {
  title: "Michigan",
  description: "Michigan football performance in national and Big Ten context.",
};

export default function MichiganPage() {
  return <MichiganHome season={CURRENT_MICHIGAN_SEASON} />;
}
