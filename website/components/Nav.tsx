import Link from "next/link";

export function Nav() {
  return (
    <header className="site-header">
      <nav className="nav shell" aria-label="Primary navigation">
        <Link className="brand" href="/" aria-label="CFB Model home">
          <span className="brand-mark">C</span>
          <span>CFB MODEL</span>
        </Link>
        <div className="nav-links">
          <Link href="/predictions">Predictions</Link>
          <Link href="/archive">Archive</Link>
          <Link href="/results">Results</Link>
          <Link href="/about">How it works</Link>
        </div>
      </nav>
    </header>
  );
}
