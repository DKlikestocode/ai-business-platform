"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { ContactableBadge } from "@/components/contactable-badge";
import { QualificationBadge } from "@/components/qualification-badge";
import { StatusBadge } from "@/components/status-badge";
import { StatusSelect } from "@/components/status-select";
import { fetchLead, updateLeadStatus } from "@/lib/api";
import {
  formatContactMethod,
  formatLeadScore,
} from "@/lib/lead-qualification";
import type { Lead, LeadStatus } from "@/lib/types";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

function DetailRow({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="detail-row">
      <dt>{label}</dt>
      <dd>{value || "—"}</dd>
    </div>
  );
}

export function LeadDetailView() {
  const params = useParams<{ id: string }>();
  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  const loadLead = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLead(params.id);
      setLead(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load lead.");
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void loadLead();
  }, [loadLead]);

  async function handleStatusChange(status: LeadStatus) {
    if (!lead) return;
    setUpdating(true);
    setError(null);
    try {
      const updated = await updateLeadStatus(lead.id, status);
      setLead(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status.");
    } finally {
      setUpdating(false);
    }
  }

  if (loading) {
    return <p className="muted">Loading lead...</p>;
  }

  if (error && !lead) {
    return <div className="alert">{error}</div>;
  }

  if (!lead) {
    return <div className="empty-state">Lead not found.</div>;
  }

  return (
    <div className="stack">
      <Link href="/leads" className="back-link">
        ← Back to leads
      </Link>

      <div className="detail-header">
        <div>
          <h2>{lead.name}</h2>
          <p className="muted">Lead ID: {lead.id}</p>
        </div>
        <StatusBadge status={lead.status} />
      </div>

      {error ? <div className="alert">{error}</div> : null}

      <div className="card">
        <h3 className="card-title">Qualification</h3>
        <dl className="detail-list">
          <div className="detail-row">
            <dt>Lead score</dt>
            <dd>
              <span className="score-pill">{formatLeadScore(lead.lead_score)}</span>
            </dd>
          </div>
          <div className="detail-row">
            <dt>Qualification status</dt>
            <dd>
              <QualificationBadge status={lead.qualification_status} />
            </dd>
          </div>
          <div className="detail-row">
            <dt>Contactable</dt>
            <dd>
              <ContactableBadge contactable={lead.contactable} />
            </dd>
          </div>
          <DetailRow
            label="Contact method"
            value={formatContactMethod(lead.contact_method)}
          />
          <DetailRow
            label="Notification sent"
            value={
              lead.notification_sent_at
                ? formatDate(lead.notification_sent_at)
                : null
            }
          />
        </dl>
      </div>

      <div className="card">
        <h3 className="card-title">Lead details</h3>
        <dl className="detail-list">
          <DetailRow label="Phone" value={lead.phone} />
          <DetailRow label="Email" value={lead.email} />
          <DetailRow label="Company" value={lead.company} />
          <DetailRow label="Location" value={lead.location} />
          <DetailRow label="Service requested" value={lead.service_requested} />
          <DetailRow label="Description" value={lead.description} />
          <DetailRow label="Urgency" value={lead.urgency} />
          <DetailRow
            label="Preferred callback"
            value={lead.preferred_callback_time}
          />
          <DetailRow label="Conversation ID" value={lead.conversation_id} />
          <DetailRow label="Created" value={formatDate(lead.created_at)} />
          <DetailRow label="Summary" value={lead.summary} />
        </dl>
      </div>

      <div className="card">
        <label className="field-block">
          <span>Update status</span>
          <StatusSelect
            value={lead.status}
            disabled={updating}
            onChange={(status) => void handleStatusChange(status)}
          />
        </label>
      </div>
    </div>
  );
}
