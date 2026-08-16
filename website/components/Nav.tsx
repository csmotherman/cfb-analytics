import Link from "next/link";

export function Nav(){
  return <nav className="nav">
    <strong>CFB Analytics Pilot</strong>
    <Link href="/">Home</Link>
    <Link href="/teams">Teams</Link>
    <Link href="/rankings">Rankings</Link>
    <Link href="/compare">Compare</Link>
    <Link href="/simulator">Simulator</Link>
    <Link href="/archetypes">Identity Explorer</Link>
    <Link href="/metrics">Metrics</Link>
  </nav>;
}
