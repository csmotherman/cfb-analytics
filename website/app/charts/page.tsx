import type {Metadata} from "next";
import {creatorChartPack} from "../../lib/creator-chart-pack";
import {CreatorCharts} from "./CreatorCharts";
import styles from "./charts.module.css";

export const metadata:Metadata={
  title:"Chart Room",
  description:"Creator-ready college football charts built from opponent-adjusted ratings, leave-one-game-out game grading, and national context.",
};

export default function ChartsPage(){
  const pack=creatorChartPack(2025);

  if(!pack){
    return <div className={styles.empty}>
      <span>CHART ROOM</span>
      <h1>Creator charts are being prepared.</h1>
      <p>The opponent-adjusted season artifact is not available in this deployment yet.</p>
    </div>;
  }

  return <CreatorCharts pack={pack}/>;
}
