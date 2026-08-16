"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { useAuth } from "@/components/auth-provider";
import { IntakeStatusBadge } from "@/components/intake-status-badge";
import { AlertBanner } from "@/components/ui/alert-banner";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { Link } from "@/i18n/navigation";
import { fetchIntakeItems, fetchIntakeSetup } from "@/lib/api";
import { formatDateTime } from "@/lib/format-datetime";
import { INTAKE_FILTER_STATUSES, intakeDisplayName } from "@/lib/intake";
import type { IntakeItem, IntakeSetup, IntakeStatus } from "@/lib/types";

export function IntakeDashboard() {
  const locale = useLocale();
  const t = useTranslations("intake");
  const { loading: authLoading } = useAuth();
  const [items, setItems] = useState<IntakeItem[]>([]);
  const [setup, setSetup] = useState<IntakeSetup | null>(null);
  const [statusFilter, setStatusFilter] = useState<IntakeStatus | "">("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadItems = useCallback(
    async (silent = false) => {
      if (!silent) setLoading(true);
      setError(null);
      try {
        const data = await fetchIntakeItems({
          page,
          page_size: 20,
          status: statusFilter,
        });
        setItems(data.items);
        setTotal(data.total);
        setTotalPages(Math.max(1, data.total_pages));
      } catch (err) {
        setError(err instanceof Error ? err.message : t("loadFailed"));
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [page, statusFilter, t],
  );

  useEffect(() => {
    if (authLoading) return;
    void loadItems();
    void fetchIntakeSetup()
      .then(setSetup)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : t("loadFailed"));
      });
  }, [authLoading, loadItems, t]);

  useEffect(() => {
    if (!items.some((item) => ["received", "processing"].includes(item.status))) {
      return;
    }
    const interval = window.setInterval(() => void loadItems(true), 4000);
    return () => window.clearInterval(interval);
  }, [items, loadItems]);

  async function copyInboundAddress() {
    if (!setup?.inbound_email) return;
    await navigator.clipboard.writeText(setup.inbound_email);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  const initialLoading = authLoading || loading;

  return (
    <div className="stack intake-page">
      <PageHeader title={t("title")} description={t("description")}>
        {setup?.inbound_email ? (
          <button
            type="button"
            className="button secondary"
            onClick={() => void copyInboundAddress()}
          >
            {copied ? t("addressCopied") : t("copyAddress")}
          </button>
        ) : null}
      </PageHeader>

      {setup?.email_enabled && setup.inbound_email ? (
        <div className="intake-address-card card">
          <div>
            <strong>{t("inboundAddressLabel")}</strong>
            <p className="muted">{t("inboundAddressHint")}</p>
          </div>
          <code>{setup.inbound_email}</code>
        </div>
      ) : setup ? (
        <AlertBanner variant="info">{t("emailNotConnected")}</AlertBanner>
      ) : null}

      <div className="toolbar">
        <label className="field-inline">
          <span>{t("filterLabel")}</span>
          <select
            className="select"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value as IntakeStatus | "");
              setPage(1);
            }}
          >
            <option value="">{t("filterAll")}</option>
            {INTAKE_FILTER_STATUSES.map((status) => (
              <option key={status} value={status}>
                {t(`statuses.${status}`)}
              </option>
            ))}
          </select>
        </label>
        <span className="muted">{t("resultCount", { count: total })}</span>
      </div>

      {error ? <AlertBanner>{error}</AlertBanner> : null}
      {initialLoading ? (
        <div className="card content-loading-panel">
          <LoadingState label={t("loading")} />
        </div>
      ) : null}

      {!initialLoading && items.length === 0 ? (
        <EmptyState
          title={statusFilter ? t("emptyFilteredTitle") : t("emptyTitle")}
          description={
            statusFilter
              ? t("emptyFilteredDescription")
              : setup?.inbound_email
                ? t("emptyDescription", { email: setup.inbound_email })
                : t("emptyDisconnectedDescription")
          }
        />
      ) : null}

      {!initialLoading && items.length > 0 ? (
        <div className="intake-list">
          {items.map((item) => (
            <Link
              key={item.id}
              href={`/intake/${item.id}`}
              className="card intake-card"
            >
              <div className="intake-card-topline">
                <div>
                  <p className="intake-card-customer">{intakeDisplayName(item)}</p>
                  <h3>{item.subject || t("noSubject")}</h3>
                </div>
                <IntakeStatusBadge status={item.status} />
              </div>
              <p className="intake-card-service muted">
                {item.service_requested || item.description || t("awaitingExtraction")}
              </p>
              <div className="intake-card-meta muted">
                <span>{t(`channels.${item.channel}`)}</span>
                <span>
                  {formatDateTime(item.received_at || item.created_at, locale) || "—"}
                </span>
                <span>{t("attachmentCount", { count: item.attachments.length })}</span>
                {item.safety_warning ? (
                  <span className="intake-card-warning">{t("safetyFlag")}</span>
                ) : null}
              </div>
            </Link>
          ))}
        </div>
      ) : null}

      {!initialLoading && totalPages > 1 ? (
        <div className="pagination">
          <button
            type="button"
            className="button secondary"
            disabled={page <= 1 || loading}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
          >
            {t("previous")}
          </button>
          <span>{t("page", { page, totalPages })}</span>
          <button
            type="button"
            className="button secondary"
            disabled={page >= totalPages || loading}
            onClick={() => setPage((current) => current + 1)}
          >
            {t("next")}
          </button>
        </div>
      ) : null}
    </div>
  );
}
