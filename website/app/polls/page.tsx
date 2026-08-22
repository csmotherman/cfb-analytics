import type {Metadata} from "next";
import {FanPoll} from "../../components/FanPoll";
import {FAN_POLLS} from "../../lib/polls";

export const metadata:Metadata={title:"Michigan Fan Polls & 2026 Predictions",description:"Vote on Michigan's 2026 record, playoff ceiling, player projections, Week 1 and more — then see how the fanbase voted."};

export default function Polls(){return <div className="polls-page">
  <section className="polls-hero"><div className="polls-shell"><span className="polls-kicker">THE FAN BOARD · 2026</span><h1>CALL IT<br/><b>BEFORE IT HAPPENS.</b></h1><p>Record. Playoff run. Player breakouts. Week 1. Make your picks and see where Michigan fans actually stand.</p><div className="polls-hero-meta"><span><b>{FAN_POLLS.length}</b> PREDICTIONS</span><span><b>1</b> VOTE / DEVICE</span><span><b>LIVE</b> COMMUNITY %</span></div></div></section>
  <main className="polls-shell polls-content"><FanPoll/></main>
</div>}
