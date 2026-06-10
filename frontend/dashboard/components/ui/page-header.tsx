import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: ReactNode;
}

export function PageHeader({ title, description, children }: PageHeaderProps) {
  return (
    <div className="page-header">
      <div className="page-intro">
        <h2 className="page-title">{title}</h2>
        {description ? <p className="muted">{description}</p> : null}
      </div>
      {children}
    </div>
  );
}
