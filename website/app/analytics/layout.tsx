import type {ReactNode} from "react";
import "../../styles/analytics-shell.css";
import "../../styles/analytics-year-wheel-fix.css";
import "../../styles/fan-overview.css";
import "../../styles/unit-detail.css";

export default function AnalyticsLayout({children}:{children:ReactNode}){
  return <div className="analytics-shell">
    <div className="wrap analytics-shell-inner">
      {children}
    </div>
  </div>;
}
