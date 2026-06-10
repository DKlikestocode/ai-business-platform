import { Link } from "@/i18n/navigation";

interface EmptyStateProps {
  title: string;
  description: string;
  actionHref?: string;
  actionLabel?: string;
}

export function EmptyState({
  title,
  description,
  actionHref,
  actionLabel,
}: EmptyStateProps) {
  return (
    <div className="empty-state-panel">
      <h3>{title}</h3>
      <p className="muted">{description}</p>
      {actionHref && actionLabel ? (
        <Link href={actionHref} className="button">
          {actionLabel}
        </Link>
      ) : null}
    </div>
  );
}
