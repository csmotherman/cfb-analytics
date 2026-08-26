type Section = readonly [id: string, label: string];

export function ArticleMobileToc({sections}:{sections:readonly Section[]}){
  return <nav className="feature-mobile-toc" aria-label="Jump to section">
    {sections.map(([id,label],index)=>
      <a key={id} href={`#${id}`}><b>{String(index+1).padStart(2,"0")}</b>{label}</a>
    )}
  </nav>;
}
