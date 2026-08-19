"use client";
import Image from "next/image";
import { useState } from "react";
import { teamLogoUrl, type TeamLogoSize } from "../../lib/team-assets";
export function TeamLogo({ teamId, name, size = 128, className = "" }: { teamId: number; name: string; size?: TeamLogoSize; className?: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) return <span className={`team-logo-fallback ${className}`} style={{ width: size, height: size }} aria-label={`${name} logo unavailable`}>{name.split(/\s+/).map((word) => word[0]).join("").slice(0, 3)}</span>;
  return <Image className={className} src={teamLogoUrl(teamId, size)} alt={`${name} logo`} width={size} height={size} unoptimized onError={() => setFailed(true)} />;
}
