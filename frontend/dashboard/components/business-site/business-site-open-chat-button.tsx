"use client";

import type { ReactNode } from "react";

import { openBusinessSiteChat } from "@/components/business-site/business-site-chat-launcher";

interface BusinessSiteOpenChatButtonProps {
  className?: string;
  children: ReactNode;
}

export function BusinessSiteOpenChatButton({
  className,
  children,
}: BusinessSiteOpenChatButtonProps) {
  return (
    <button type="button" className={className} onClick={openBusinessSiteChat}>
      {children}
    </button>
  );
}
