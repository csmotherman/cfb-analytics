import type {ReactNode} from "react";

export default function MichiganWesternMichiganPreviewLayout({children}:{children:ReactNode}){
  return <>
    <div style={{background:"#02111f",padding:"18px 18px 0"}}>
      <div style={{width:"min(1180px,100%)",margin:"0 auto"}}>
        <img
          src="/images/articles/michigan-western-michigan-2026-preview.jpg"
          alt="Michigan vs. Western Michigan game preview"
          style={{display:"block",width:"100%",height:"auto",aspectRatio:"16 / 9",objectFit:"cover",borderRadius:18,border:"1px solid #26435b",boxShadow:"0 24px 60px rgba(0,0,0,.28)"}}
        />
      </div>
    </div>
    {children}
  </>;
}
