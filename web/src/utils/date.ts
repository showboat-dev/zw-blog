export function formatDate(date: string | null): string {
  if (!date) return "";
  const d = new Date(date);
  const month = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${d.getUTCFullYear()} / ${month}.${day}`;
}
