"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";

import { IntakeStatusBadge } from "@/components/intake-status-badge";
import { AlertBanner } from "@/components/ui/alert-banner";
import { LoadingState } from "@/components/ui/loading-state";
import { Link } from "@/i18n/navigation";
import {
  downloadIntakeAttachment,
  downloadIntakeSource,
  exportIntakeCsv,
  fetchIntakeItem,
  retryIntakeItem,
  reviewIntakeItem,
} from "@/lib/api";
import { formatDateTime } from "@/lib/format-datetime";
import {
  canExportIntake,
  canReviewIntake,
  formatFileSize,
  intakeDisplayName,
} from "@/lib/intake";
import type {
  IntakeItem,
  IntakeKind,
  IntakeRecommendedAction,
  IntakeReviewDecision,
  IntakeReviewRequest,
  IntakeScope,
  IntakeUrgency,
} from "@/lib/types";

interface IntakeFormState {
  customer_name: string;
  customer_company: string;
  customer_email: string;
  customer_phone: string;
  street: string;
  postal_code: string;
  city: string;
  service_requested: string;
  description: string;
  urgency: IntakeUrgency;
  preferred_time: string;
  inquiry_kind: IntakeKind;
  inquiry_scope: IntakeScope;
  recommended_action: IntakeRecommendedAction;
}

function createForm(item: IntakeItem): IntakeFormState {
  return {
    customer_name: item.customer_name || "",
    customer_company: item.customer_company || "",
    customer_email: item.customer_email || item.sender_email || "",
    customer_phone: item.customer_phone || "",
    street: item.service_address?.street || "",
    postal_code: item.service_address?.postal_code || "",
    city: item.service_address?.city || "",
    service_requested: item.service_requested || "",
    description: item.description || "",
    urgency: item.urgency || "unknown",
    preferred_time: item.preferred_time || "",
    inquiry_kind: item.inquiry_kind || "other",
    inquiry_scope: item.inquiry_scope || "unclear",
    recommended_action: item.recommended_action || "manual_route",
  };
}

function nullable(value: string): string | null {
  return value.trim() || null;
}

function buildReviewPayload(
  form: IntakeFormState,
  decision: IntakeReviewDecision,
): IntakeReviewRequest {
  return {
    decision,
    customer_name: nullable(form.customer_name),
    customer_company: nullable(form.customer_company),
    customer_email: nullable(form.customer_email),
    customer_phone: nullable(form.customer_phone),
    service_address: {
      street: nullable(form.street),
      postal_code: nullable(form.postal_code),
      city: nullable(form.city),
    },
    service_requested: nullable(form.service_requested),
    description: nullable(form.description),
    urgency: form.urgency,
    preferred_time: nullable(form.preferred_time),
    inquiry_kind: form.inquiry_kind,
    inquiry_scope: form.inquiry_scope,
    recommended_action: form.recommended_action,
  };
}

export function IntakeDetailView() {
  const params = useParams<{ id: string }>();
  const itemId = Array.isArray(params.id) ? params.id[0] : params.id;
  const locale = useLocale();
  const t = useTranslations("intakeDetail");
  const tIntake = useTranslations("intake");
  const [item, setItem] = useState<IntakeItem | null>(null);
  const [form, setForm] = useState<IntakeFormState | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadItem = useCallback(
    async (silent = false) => {
      if (!itemId) {
        setError(t("notFound"));
        setLoading(false);
        return;
      }
      if (!silent) setLoading(true);
      try {
        const data = await fetchIntakeItem(itemId);
        setItem(data);
        setForm(createForm(data));
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : t("loadFailed"));
      } finally {
        if (!silent) setLoading(false);
      }
    },
    [itemId, t],
  );

  useEffect(() => {
    void loadItem();
  }, [loadItem]);

  useEffect(() => {
    if (!item || !["received", "processing"].includes(item.status)) return;
    const interval = window.setInterval(() => void loadItem(true), 3000);
    return () => window.clearInterval(interval);
  }, [item, loadItem]);

  function updateField<K extends keyof IntakeFormState>(
    field: K,
    value: IntakeFormState[K],
  ) {
    setForm((current) => (current ? { ...current, [field]: value } : current));
  }

  async function handleDecision(decision: IntakeReviewDecision) {
    if (!item || !form) return;
    if (decision === "discard" && !window.confirm(t("discardConfirm"))) return;
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await reviewIntakeItem(
        item.id,
        buildReviewPayload(form, decision),
      );
      setItem(updated);
      setForm(createForm(updated));
      setSuccess(
        decision === "approve"
          ? t("approvedSuccess")
          : decision === "discard"
            ? t("discardedSuccess")
            : t("savedSuccess"),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : t("updateFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function handleRetry() {
    if (!item) return;
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await retryIntakeItem(item.id);
      setItem(updated);
      setSuccess(t("retrySuccess"));
    } catch (err) {
      setError(err instanceof Error ? err.message : t("retryFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function runDownload(
    action: () => Promise<void>,
    failure: string,
  ): Promise<boolean> {
    setBusy(true);
    setError(null);
    try {
      await action();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : failure);
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function handleExport() {
    if (!item) return;
    const exported = await runDownload(
      () => exportIntakeCsv(item.id),
      t("exportFailed"),
    );
    if (exported) await loadItem(true);
  }

  const reviewable = item ? canReviewIntake(item.status) : false;
  const disabled = busy || !reviewable;

  return (
    <div className="stack intake-detail-page">
      <Link href="/intake" className="back-link">
        {t("back")}
      </Link>

      {loading ? (
        <div className="card content-loading-panel">
          <LoadingState label={t("loading")} />
        </div>
      ) : null}
      {!loading && error && !item ? <AlertBanner>{error}</AlertBanner> : null}
      {!loading && !item ? <div className="empty-state">{t("notFound")}</div> : null}

      {!loading && item && form ? (
        <>
          <div className="detail-header intake-detail-header">
            <div>
              <p className="muted intake-detail-eyebrow">
                {tIntake(`channels.${item.channel}`)} · {formatDateTime(
                  item.received_at || item.created_at,
                  locale,
                  "full",
                )}
              </p>
              <h2>{item.subject || tIntake("noSubject")}</h2>
              <p className="muted">{intakeDisplayName(item)}</p>
            </div>
            <IntakeStatusBadge status={item.status} />
          </div>

          {error ? <AlertBanner>{error}</AlertBanner> : null}
          {success ? <AlertBanner variant="success">{success}</AlertBanner> : null}
          {item.safety_warning ? (
            <AlertBanner>{t("safetyWarning", { warning: item.safety_warning })}</AlertBanner>
          ) : null}
          {item.processing_error ? (
            <AlertBanner>{t("processingError", { error: item.processing_error })}</AlertBanner>
          ) : null}
          {["received", "processing"].includes(item.status) ? (
            <AlertBanner variant="info">{t("processingNotice")}</AlertBanner>
          ) : null}
          {item.review_reasons.length > 0 ? (
            <section className="card intake-review-reasons">
              <h3>{t("reviewReasons")}</h3>
              <ul>
                {item.review_reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </section>
          ) : null}

          {form.customer_phone || form.customer_email ? (
            <section className="card intake-contact-card">
              <h3>{t("contactTitle")}</h3>
              <div className="intake-contact-actions">
                {form.customer_phone ? (
                  <a className="button" href={`tel:${form.customer_phone}`}>
                    {t("callCustomer")}
                  </a>
                ) : null}
                {form.customer_email ? (
                  <a className="button secondary" href={`mailto:${form.customer_email}`}>
                    {t("emailCustomer")}
                  </a>
                ) : null}
              </div>
            </section>
          ) : null}

          {item.channel === "email" ? (
            <section className="card intake-source-card">
              <div>
                <h3>{t("sourceTitle")}</h3>
                <p className="muted">
                  {item.sender_name || "—"} &lt;{item.sender_email || "—"}&gt;
                </p>
              </div>
              <button
                type="button"
                className="button secondary"
                disabled={busy}
                onClick={() =>
                  void runDownload(
                    () => downloadIntakeSource(item.id),
                    t("sourceDownloadFailed"),
                  )
                }
              >
                {t("downloadSource")}
              </button>
            </section>
          ) : null}

          {item.attachments.length > 0 ? (
            <section className="card">
              <h3>{t("attachmentsTitle")}</h3>
              <div className="intake-attachment-list">
                {item.attachments.map((attachment) => (
                  <button
                    key={attachment.id}
                    type="button"
                    className="intake-attachment-button"
                    disabled={busy}
                    onClick={() =>
                      void runDownload(
                        () =>
                          downloadIntakeAttachment(
                            item.id,
                            attachment.id,
                            attachment.filename,
                          ),
                        t("attachmentDownloadFailed"),
                      )
                    }
                  >
                    <span>{attachment.filename}</span>
                    <span className="muted">
                      {formatFileSize(attachment.size_bytes, locale)}
                    </span>
                  </button>
                ))}
              </div>
            </section>
          ) : null}

          <form className="card intake-review-form" onSubmit={(event) => event.preventDefault()}>
            <div>
              <h3>{t("formTitle")}</h3>
              <p className="muted">{t("formDescription")}</p>
            </div>

            <div className="intake-form-grid">
              <label className="field">
                <span>{t("customerName")}</span>
                <input
                  className="input"
                  value={form.customer_name}
                  disabled={disabled}
                  onChange={(event) => updateField("customer_name", event.target.value)}
                />
              </label>
              <label className="field">
                <span>{t("customerCompany")}</span>
                <input
                  className="input"
                  value={form.customer_company}
                  disabled={disabled}
                  onChange={(event) => updateField("customer_company", event.target.value)}
                />
              </label>
              <label className="field">
                <span>{t("customerEmail")}</span>
                <input
                  className="input"
                  type="email"
                  value={form.customer_email}
                  disabled={disabled}
                  onChange={(event) => updateField("customer_email", event.target.value)}
                />
              </label>
              <label className="field">
                <span>{t("customerPhone")}</span>
                <input
                  className="input"
                  type="tel"
                  value={form.customer_phone}
                  disabled={disabled}
                  onChange={(event) => updateField("customer_phone", event.target.value)}
                />
              </label>
            </div>

            <fieldset className="intake-fieldset" disabled={disabled}>
              <legend>{t("address")}</legend>
              <div className="intake-form-grid intake-address-grid">
                <label className="field">
                  <span>{t("street")}</span>
                  <input
                    className="input"
                    value={form.street}
                    onChange={(event) => updateField("street", event.target.value)}
                  />
                </label>
                <label className="field">
                  <span>{t("postalCode")}</span>
                  <input
                    className="input"
                    value={form.postal_code}
                    onChange={(event) => updateField("postal_code", event.target.value)}
                  />
                </label>
                <label className="field">
                  <span>{t("city")}</span>
                  <input
                    className="input"
                    value={form.city}
                    onChange={(event) => updateField("city", event.target.value)}
                  />
                </label>
              </div>
            </fieldset>

            <label className="field">
              <span>{t("serviceRequested")}</span>
              <input
                className="input"
                value={form.service_requested}
                disabled={disabled}
                onChange={(event) => updateField("service_requested", event.target.value)}
              />
            </label>
            <label className="field">
              <span>{t("description")}</span>
              <textarea
                className="input intake-textarea"
                rows={6}
                value={form.description}
                disabled={disabled}
                onChange={(event) => updateField("description", event.target.value)}
              />
            </label>

            <div className="intake-form-grid intake-select-grid">
              <label className="field">
                <span>{t("urgency")}</span>
                <select
                  className="select"
                  value={form.urgency}
                  disabled={disabled}
                  onChange={(event) =>
                    updateField("urgency", event.target.value as IntakeUrgency)
                  }
                >
                  {(["high", "medium", "low", "unknown"] as IntakeUrgency[]).map(
                    (value) => (
                      <option key={value} value={value}>
                        {t(`urgencies.${value}`)}
                      </option>
                    ),
                  )}
                </select>
              </label>
              <label className="field">
                <span>{t("preferredTime")}</span>
                <input
                  className="input"
                  value={form.preferred_time}
                  disabled={disabled}
                  onChange={(event) => updateField("preferred_time", event.target.value)}
                />
              </label>
              <label className="field">
                <span>{t("inquiryKind")}</span>
                <select
                  className="select"
                  value={form.inquiry_kind}
                  disabled={disabled}
                  onChange={(event) =>
                    updateField("inquiry_kind", event.target.value as IntakeKind)
                  }
                >
                  {(["appointment_consultation", "quote", "other"] as IntakeKind[]).map(
                    (value) => (
                      <option key={value} value={value}>
                        {t(`kinds.${value}`)}
                      </option>
                    ),
                  )}
                </select>
              </label>
              <label className="field">
                <span>{t("scope")}</span>
                <select
                  className="select"
                  value={form.inquiry_scope}
                  disabled={disabled}
                  onChange={(event) =>
                    updateField("inquiry_scope", event.target.value as IntakeScope)
                  }
                >
                  {(["in_scope", "out_of_scope", "unclear"] as IntakeScope[]).map(
                    (value) => (
                      <option key={value} value={value}>
                        {t(`scopes.${value}`)}
                      </option>
                    ),
                  )}
                </select>
              </label>
              <label className="field">
                <span>{t("recommendedAction")}</span>
                <select
                  className="select"
                  value={form.recommended_action}
                  disabled={disabled}
                  onChange={(event) =>
                    updateField(
                      "recommended_action",
                      event.target.value as IntakeRecommendedAction,
                    )
                  }
                >
                  {(
                    [
                      "call_immediately",
                      "schedule_visit",
                      "prepare_quote",
                      "request_missing_information",
                      "manual_route",
                      "discard_spam",
                      "merge_duplicate",
                    ] as IntakeRecommendedAction[]
                  ).map((value) => (
                    <option key={value} value={value}>
                      {t(`actions.${value}`)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="intake-form-actions">
              {reviewable ? (
                <>
                  <button
                    type="button"
                    className="button secondary"
                    disabled={busy}
                    onClick={() => void handleDecision("save_for_review")}
                  >
                    {t("saveForReview")}
                  </button>
                  <button
                    type="button"
                    className="button"
                    disabled={busy}
                    onClick={() => void handleDecision("approve")}
                  >
                    {t("approve")}
                  </button>
                  <button
                    type="button"
                    className="button intake-danger-button"
                    disabled={busy}
                    onClick={() => void handleDecision("discard")}
                  >
                    {t("discard")}
                  </button>
                </>
              ) : null}
              {item.status === "failed" ? (
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => void handleRetry()}
                >
                  {t("retry")}
                </button>
              ) : null}
              {canExportIntake(item.status) ? (
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => void handleExport()}
                >
                  {t("exportCsv")}
                </button>
              ) : null}
            </div>
          </form>
        </>
      ) : null}
    </div>
  );
}
