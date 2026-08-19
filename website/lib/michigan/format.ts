export function classLabel(year?: number | null): string {
  return ({ 1: "Freshman", 2: "Sophomore", 3: "Junior", 4: "Senior", 5: "Graduate" } as Record<number, string>)[year ?? 0] ?? "Class unavailable";
}
export function formatHeight(inches?: number | null): string {
  return inches ? `${Math.floor(inches / 12)}'${inches % 12}\"` : "—";
}
