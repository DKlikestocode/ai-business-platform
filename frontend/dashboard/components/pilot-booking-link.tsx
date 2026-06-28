"use client";

import type { ReactNode } from "react";

import {
  getPilotBookingUrl,
  isExternalPilotBookingUrl,
} from "@/lib/pilot-booking";

interface PilotBookingLinkProps {
  className?: string;
  children: ReactNode;
}

export function PilotBookingLink({ className, children }: PilotBookingLinkProps) {
  const url = getPilotBookingUrl();
  const external = isExternalPilotBookingUrl(url);

  return (
    <a
      href={url}
      className={className}
      {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
    >
      {children}
    </a>
  );
}
