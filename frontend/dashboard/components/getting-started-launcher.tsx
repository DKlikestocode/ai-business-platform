"use client";

import { useTranslations } from "next-intl";

import { GettingStartedPanel } from "@/components/getting-started-panel";
import { GettingStartedOverlay } from "@/components/getting-started-overlay";
import { useGettingStartedNavVisibility } from "@/lib/use-getting-started-nav-visibility";

export function GettingStartedLauncher() {
  const { showGettingStarted } = useGettingStartedNavVisibility();
  const t = useTranslations("gettingStarted");

  return (
    <GettingStartedOverlay
      visible={showGettingStarted}
      autoOpen
      title={t("overlayTitle")}
      subtitle={t("overlaySubtitle")}
      closeLabel={t("overlayClose")}
      launcherLabel={t("overlayLauncher")}
      progressLabel={t("overlayProgressFallback")}
    >
      <GettingStartedPanel />
    </GettingStartedOverlay>
  );
}
