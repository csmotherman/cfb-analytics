import type {Metadata} from "next";
import {creatorGameLibrary} from "../../lib/creator-game-library";
import {CreatorCharts} from "./CreatorCharts";
import styles from "./charts.module.css";

export const metadata:Metadata={
  title:"2025 Michigan Game Chart Room",
  description:"Audience-first, opponent-adjusted breakdowns for every Michigan game in 2025, including two-way performance versus expectation and opponent strength context.",
};

export default function ChartsPage(){
  const library=creatorGameLibrary(2025);

  if(!library){
    return <div className={styles.empty}>
      <span>CHART ROOM</span>
      <h1>Game dossiers are being prepared.</h1>
      <p>The opponent-adjusted season artifact is not available in this deployment yet.</p>
    </div>;
  }

  return <CreatorCharts library={library}/>;
}
