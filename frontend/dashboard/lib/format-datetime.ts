export function formatDateTime(
  value: string | null | undefined,
  locale: string,
  dateStyle: "full" | "medium" = "medium",
): string | null {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat(locale, {
    dateStyle,
    timeStyle: "short",
  }).format(date);
}
