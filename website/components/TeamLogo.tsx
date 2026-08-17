type TeamLogoProps = {
  team: string;
  src?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
};

function initials(team: string): string {
  const parts = team.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[parts.length - 1][0] ?? ""}`.toUpperCase();
}

export function TeamLogo({ team, src, size = "md", className = "" }: TeamLogoProps) {
  const classes = `team-logo team-logo-${size}${className ? ` ${className}` : ""}`;
  return (
    <span className={classes} aria-hidden="true">
      {src ? (
        <img src={src} alt="" loading="lazy" decoding="async" />
      ) : (
        <span>{initials(team)}</span>
      )}
    </span>
  );
}
