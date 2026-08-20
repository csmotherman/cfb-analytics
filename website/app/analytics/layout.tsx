import type {ReactNode} from "react";
import "../../styles/analytics-shell.css";

export default function AnalyticsLayout({children}:{children:ReactNode}){
  return <div className="analytics-shell">
    <div className="wrap analytics-shell-inner">
      {children}
    </div>
  </div>;
}
