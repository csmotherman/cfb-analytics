type Point={label:string;value:number};
function Bars({points}:{points:Point[]}){const max=Math.max(1,...points.map(p=>Math.abs(p.value)));return <div className="chart-bars" role="img" aria-label={points.map(p=>`${p.label} ${p.value}`).join(", ")}>{points.map(p=><div key={p.label}><span>{p.label}</span><i><b style={{width:`${Math.abs(p.value)/max*100}%`}}/></i><strong>{p.value}</strong></div>)}</div>}
export function MetricTrendChart({points}:{points:Point[]}){return <Bars points={points}/>}
export function TeamComparisonChart({points}:{points:Point[]}){return <Bars points={points}/>}
export function PlayerTrendChart({points}:{points:Point[]}){return <Bars points={points}/>}
export function SeasonHistoryChart({points}:{points:Point[]}){return <Bars points={points}/>}
export function OpponentComparisonChart({points}:{points:Point[]}){return <Bars points={points}/>}
export function ScatterLogoChart(){return <div className="empty-state"><span>TEAM COMPARISON</span><h2>Chart coming soon.</h2><p>See how Michigan stacks up across college football.</p></div>}
