import { contactableBadgeClass, formatContactable } from "@/lib/lead-qualification";

interface ContactableBadgeProps {
  contactable: boolean;
}

export function ContactableBadge({ contactable }: ContactableBadgeProps) {
  return (
    <span className={`badge ${contactableBadgeClass(contactable)}`}>
      {formatContactable(contactable)}
    </span>
  );
}
