import Link from "next/link";

export function Nav() {
  return (
    <header className="site-header">
      <nav className="nav shell" aria-label="Primary navigation">
        <Link className="brand" href="/" aria-label="Beat the Model home">
          <span className="brand-mark">B</span>
          <span>BEAT THE MODEL</span>
        </Link>
        <div className="nav-links">
          <Link href="/play">Play</Link>
          <Link href="/rankings">Rankings</Link>
          <Link href="/archive">Archive</Link>
          <Link href="/about">How it works</Link>
        </div>
      </nav>
    </header>
  );
}
