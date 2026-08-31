import {ImageResponse} from "next/og";
import {teamLogoUrl} from "../../../../lib/team-assets";
import {michiganWesternMichigan2026 as data} from "../../../../lib/michigan/matchup-preview-data";

export const runtime="edge";

const NAVY="#06111d";
const PANEL="#0d2032";
const PANEL_2="#10273b";
const MAIZE="#ffcb05";
const WHITE="#f7f9fb";
const MUTED="#93a7b9";
const LINE="rgba(255,255,255,0.10)";

async function loadGoogleFont(family:string,weight:number):Promise<ArrayBuffer|null>{
  try{
    const css=await(await fetch(`https://fonts.googleapis.com/css2?family=${encodeURIComponent(family)}:wght@${weight}`)).text();
    const match=css.match(/src: url\(([^)]+)\) format\('(?:opentype|truetype)'\)/);
    if(!match)return null;
    const res=await fetch(match[1]);
    return res.status===200?await res.arrayBuffer():null;
  }catch{return null;}
}

function Metric({value,label,detail,accent=false}:{value:string;label:string;detail:string;accent?:boolean}){
  return <div style={{display:"flex",flexDirection:"column",flex:1,minHeight:154,padding:"22px 24px",border:`1px solid ${LINE}`,borderRadius:16,backgroundColor:PANEL}}>
    <div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:43,fontWeight:800,lineHeight:1,color:accent?MAIZE:WHITE}}>{value}</div>
    <div style={{display:"flex",marginTop:9,fontFamily:"Inter",fontSize:15,fontWeight:800,letterSpacing:1.1,color:WHITE,textTransform:"uppercase"}}>{label}</div>
    <div style={{display:"flex",marginTop:8,fontFamily:"Inter",fontSize:14,fontWeight:500,lineHeight:1.35,color:MUTED}}>{detail}</div>
  </div>;
}

function SnapBar({label,pct}:{label:string;pct:number}){
  return <div style={{display:"flex",alignItems:"center",width:"100%",marginTop:13}}>
    <div style={{display:"flex",width:38,fontFamily:"Inter",fontSize:14,fontWeight:800,color:WHITE}}>{label}</div>
    <div style={{display:"flex",flex:1,height:9,borderRadius:8,backgroundColor:"rgba(255,255,255,0.08)",overflow:"hidden"}}><div style={{display:"flex",width:`${pct}%`,height:"100%",borderRadius:8,backgroundColor:MAIZE}}/></div>
    <div style={{display:"flex",justifyContent:"flex-end",width:54,fontFamily:"Barlow Condensed",fontSize:24,fontWeight:800,color:WHITE}}>{pct}%</div>
  </div>;
}

export async function GET(){
  const b=data.blueprint;
  const [barlowBold,interRegular,interBold]=await Promise.all([loadGoogleFont("Barlow Condensed",800),loadGoogleFont("Inter",400),loadGoogleFont("Inter",700)]);
  const fonts=[
    barlowBold&&{name:"Barlow Condensed",data:barlowBold,weight:800 as const,style:"normal" as const},
    interRegular&&{name:"Inter",data:interRegular,weight:400 as const,style:"normal" as const},
    interBold&&{name:"Inter",data:interBold,weight:700 as const,style:"normal" as const},
  ].filter((font):font is NonNullable<typeof font>=>Boolean(font));

  const snaps=data.continuity.opponentExternal;
  const dl=snaps.defensePositions.find(item=>item.group==="DL")?.pct??0;
  const lb=snaps.defensePositions.find(item=>item.group==="LB")?.pct??0;
  const db=snaps.defensePositions.find(item=>item.group==="DB")?.pct??0;
  const westernPass=b.opponentOffenseVsMichiganDefense.find(row=>row.metric==="Pass success")?.opponent;

  return new ImageResponse(
    <div style={{display:"flex",flexDirection:"column",width:1600,height:900,padding:"0 64px",backgroundImage:"radial-gradient(circle at 15% 0%, #17334d 0%, transparent 35%), linear-gradient(150deg, #081725 0%, #030a12 76%)",fontFamily:"Inter",color:WHITE}}>
      <div style={{display:"flex",position:"absolute",left:0,right:0,top:0,height:6,backgroundColor:MAIZE}}/>

      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",height:86,borderBottom:`1px solid ${LINE}`}}>
        <div style={{display:"flex",alignItems:"center",gap:12}}>
          <div style={{display:"flex",width:11,height:11,borderRadius:6,backgroundColor:MAIZE}}/>
          <div style={{display:"flex",fontFamily:"Inter",fontSize:17,fontWeight:700,letterSpacing:2,color:WHITE}}>MICHIGAN FOOTBALL FOCUS</div>
        </div>
        <div style={{display:"flex",fontFamily:"Inter",fontSize:15,fontWeight:700,letterSpacing:2.2,color:MAIZE}}>WEEK 1 · SEPT. 5, 2026 · THE BIG HOUSE</div>
      </div>

      <div style={{display:"flex",alignItems:"center",padding:"31px 0 23px"}}>
        <div style={{display:"flex",alignItems:"center",justifyContent:"center",width:112,height:112,borderRadius:22,backgroundColor:"rgba(255,255,255,0.035)",border:`1px solid ${LINE}`}}><img src={teamLogoUrl(data.michiganTeamId,256)} width={86} height={86} alt=""/></div>
        <div style={{display:"flex",flexDirection:"column",flex:1,padding:"0 30px"}}>
          <div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:58,fontWeight:800,lineHeight:.95,color:WHITE}}>MICHIGAN <span style={{display:"flex",padding:"0 13px",color:MUTED}}>vs</span> WESTERN MICHIGAN</div>
          <div style={{display:"flex",marginTop:12,fontFamily:"Inter",fontSize:16,fontWeight:700,letterSpacing:1.6,color:MUTED}}>THE WEEK 1 MATCHUP STORY</div>
        </div>
        <div style={{display:"flex",alignItems:"center",justifyContent:"center",width:112,height:112,borderRadius:22,backgroundColor:"rgba(255,255,255,0.035)",border:`1px solid ${LINE}`}}><img src={teamLogoUrl(data.opponentTeamId,256)} width={86} height={86} alt=""/></div>
      </div>

      <div style={{display:"flex",marginBottom:25,padding:"20px 24px",borderLeft:`5px solid ${MAIZE}`,backgroundColor:"rgba(255,203,5,0.055)"}}>
        <div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:37,fontWeight:800,lineHeight:1.15,color:WHITE}}>Western returns the pieces that make the offense work. <span style={{display:"flex",marginLeft:9,color:MAIZE}}>The front seven is the question.</span></div>
      </div>

      <div style={{display:"flex",gap:22,flex:1,minHeight:0}}>
        <div style={{display:"flex",flexDirection:"column",width:965}}>
          <div style={{display:"flex",fontFamily:"Inter",fontSize:13,fontWeight:700,letterSpacing:1.8,color:MAIZE,marginBottom:12}}>WHY THIS GAME LOOKS THE WAY IT DOES</div>
          <div style={{display:"flex",gap:13}}>
            <Metric value={`${b.opponentSeason.rushDecisionRatePct.toFixed(1)}%`} label="WMU rush decision rate" detail="The offense wants to keep this game on the ground." accent/>
            <Metric value={`#${westernPass?.rank??118}`} label="Adjusted pass success" detail="Western's clearest 2025 efficiency weakness."/>
            <Metric value={`#${b.opponentSeason.defense.rank}`} label="WMU defense" detail="The stronger half of the 2025 team was real."/>
          </div>

          <div style={{display:"flex",alignItems:"stretch",gap:13,marginTop:13}}>
            <div style={{display:"flex",flexDirection:"column",flex:1,padding:"20px 24px",border:`1px solid ${LINE}`,borderRadius:16,backgroundColor:PANEL_2}}>
              <div style={{display:"flex",fontFamily:"Inter",fontSize:12,fontWeight:700,letterSpacing:1.5,color:MUTED}}>WESTERN DEFENSE · RETURNING 2025 SNAPS</div>
              <div style={{display:"flex",alignItems:"baseline",gap:20,marginTop:8}}><div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:48,fontWeight:800,color:MAIZE}}>{snaps.defenseOverallPct}%</div><div style={{display:"flex",fontFamily:"Inter",fontSize:15,fontWeight:600,color:WHITE}}>overall</div></div>
              <SnapBar label="DL" pct={dl}/><SnapBar label="LB" pct={lb}/><SnapBar label="DB" pct={db}/>
              <div style={{display:"flex",marginTop:12,fontFamily:"Inter",fontSize:13,fontWeight:500,lineHeight:1.35,color:MUTED}}>CBS Sports, snap-weighted. The back end returns far more game experience than the front.</div>
            </div>
            <div style={{display:"flex",flexDirection:"column",width:315,padding:"20px 22px",border:`1px solid ${LINE}`,borderRadius:16,backgroundColor:PANEL}}>
              <div style={{display:"flex",fontFamily:"Inter",fontSize:12,fontWeight:700,letterSpacing:1.4,color:MUTED}}>THE MATCHUP TO WATCH</div>
              <div style={{display:"flex",marginTop:12,fontFamily:"Barlow Condensed",fontSize:33,fontWeight:800,lineHeight:1.05,color:WHITE}}>MAKE WESTERN THROW.</div>
              <div style={{display:"flex",marginTop:12,fontFamily:"Inter",fontSize:14,fontWeight:500,lineHeight:1.45,color:MUTED}}>Michigan doesn't need to erase the run. It needs to create enough bad down-and-distance situations that Western can't live in its preferred script.</div>
            </div>
          </div>
        </div>

        <div style={{display:"flex",flexDirection:"column",flex:1,padding:"25px 27px",border:`1px solid rgba(255,203,5,.26)`,borderRadius:18,backgroundImage:"linear-gradient(155deg, rgba(255,203,5,.09), rgba(13,32,50,.92) 40%)"}}>
          <div style={{display:"flex",fontFamily:"Inter",fontSize:12,fontWeight:700,letterSpacing:1.8,color:MAIZE}}>MFF MODEL</div>
          <div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:28,fontWeight:800,color:WHITE,marginTop:6}}>MICHIGAN IS A HEAVY FAVORITE.</div>
          <div style={{display:"flex",flexDirection:"column",padding:"22px 0",marginTop:16,borderTop:`1px solid ${LINE}`,borderBottom:`1px solid ${LINE}`}}>
            <div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:76,fontWeight:800,lineHeight:.9,color:MAIZE}}>{b.winProbMichiganPct}%</div>
            <div style={{display:"flex",marginTop:8,fontFamily:"Inter",fontSize:14,fontWeight:700,color:WHITE}}>MICHIGAN WIN PROBABILITY</div>
          </div>
          <div style={{display:"flex",justifyContent:"space-between",padding:"19px 0",borderBottom:`1px solid ${LINE}`}}><div style={{display:"flex",flexDirection:"column"}}><span style={{display:"flex",fontFamily:"Inter",fontSize:11,fontWeight:700,color:MUTED}}>PROJECTED MARGIN</span><b style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:34,fontWeight:800,color:WHITE,marginTop:5}}>+27.6</b></div><div style={{display:"flex",flexDirection:"column",alignItems:"flex-end"}}><span style={{display:"flex",fontFamily:"Inter",fontSize:11,fontWeight:700,color:MUTED}}>MARKET</span><b style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:34,fontWeight:800,color:WHITE,marginTop:5}}>{data.market?.spread.replace("Michigan ","")??"—"}</b></div></div>
          <div style={{display:"flex",marginTop:18,fontFamily:"Inter",fontSize:13,fontWeight:500,lineHeight:1.45,color:MUTED}}>The model says Michigan should win comfortably. The preview explains the specific football path Western has to keep that from happening.</div>
        </div>
      </div>

      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",height:76,marginTop:20,borderTop:`1px solid ${LINE}`}}>
        <div style={{display:"flex",fontFamily:"Barlow Condensed",fontSize:22,fontWeight:800,letterSpacing:.7,color:WHITE}}>FULL BREAKDOWN → MICHIGANFOOTBALLFOCUS.COM</div>
        <div style={{display:"flex",fontFamily:"Inter",fontSize:12,fontWeight:500,color:MUTED}}>2025 opponent-adjusted model · MFF roster audit · CBS returning snaps · market labeled separately</div>
      </div>
    </div>,
    {width:1600,height:900,fonts}
  );
}