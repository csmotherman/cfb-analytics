import type {ReactNode} from "react";
import {AnalyticsNav} from "../../components/AnalyticsNav";
import "../../styles/analytics-shell.css";

export default function AnalyticsLayout({children}:{children:ReactNode}){
  return <div className="analytics-shell">
    <div className="wrap analytics-shell-inner">
      <AnalyticsNav/>
      {children}
    </div>
  </div>;
}
