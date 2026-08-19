export type TeamLogoSize = 64 | 128 | 256;

export function teamLogoUrl(teamId: number, size: TeamLogoSize = 128) {
  return `https://cdn.collegefootballdata.com/logos/${size}/${teamId}.png`;
}
