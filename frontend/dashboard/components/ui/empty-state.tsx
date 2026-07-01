import { Link } from "@/i18n/navigation";

interface EmptyStateProps {
  title: string;
  description: string;
  actionHref?: string;
  actionLabel?: string;
  secondaryActionHref?: string;
  secondaryActionLabel?: string;
  linkHref?: string;
  linkLabel?: string;
  linkOnClick?: () => void;
}

export function EmptyState({
  title,
  description,
  actionHref,
  actionLabel,
  secondaryActionHref,
  secondaryActionLabel,
  linkHref,
  linkLabel,
  linkOnClick,
}: EmptyStateProps) {
  const hasActions = actionHref && actionLabel;
  const hasSecondary = secondaryActionHref && secondaryActionLabel;

  return (
    <div className="empty-state-panel">
      <h3>{title}</h3>
      <p className="muted">{description}</p>
      {hasActions || hasSecondary ? (
        <div className="empty-state-actions">
          {hasActions ? (
            <Link href={actionHref} className="button">
              {actionLabel}
            </Link>
          ) : null}
          {hasSecondary ? (
            <Link href={secondaryActionHref} className="button secondary">
              {secondaryActionLabel}
            </Link>
          ) : null}
        </div>
      ) : null}
      {linkLabel && linkOnClick ? (
        <button type="button" className="empty-state-link" onClick={linkOnClick}>
          {linkLabel}
        </button>
      ) : linkHref && linkLabel ? (
        <Link href={linkHref} className="empty-state-link">
          {linkLabel}
        </Link>
      ) : null}
    </div>
  );
}
