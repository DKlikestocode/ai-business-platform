export type LeadStatus = "new" | "contacted" | "qualified" | "won" | "lost";
export type InquiryKind = "appointment_consultation" | "quote" | "unknown";

export type AppointmentConfirmationPreference = "email" | "sms" | "none";

export type QualificationStatus = "incomplete" | "contactable" | "qualified";

export type ContactMethod = "phone" | "email" | "channel" | "unknown";

export type CompanyTradeId = "skh";

export type UserRole = "owner" | "admin" | "member";

export type ActivationStatus =
  | "setup_incomplete"
  | "awaiting_widget"
  | "live"
  | "stale";

export interface ActivationInstall {
  company_slug: string;
  embed_snippet: string;
}

export interface CompanyActivation {
  status: ActivationStatus;
  notification_configured: boolean;
  website_url: string | null;
  widget_live_at: string | null;
  widget_last_seen_at: string | null;
  widget_last_origin: string | null;
  first_website_inquiry_at: string | null;
  install: ActivationInstall;
  updated_at: string;
}

export interface CompanyActivationUpdate {
  website_url?: string | null;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  email: string;
  phone: string | null;
  created_at: string;
}

export interface CompanyCreateRequest {
  name: string;
  email: string;
  phone?: string;
}

export interface UserCreateRequest {
  company_id: string;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  role?: UserRole;
}

export interface UserCreateResponse {
  id: string;
  company_id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface CompanySettings {
  name: string;
  slug: string;
  email: string;
  phone: string | null;
  notification_email: string | null;
  notification_min_urgency: "high" | "medium" | "low";
  service_area_center: string | null;
  service_radius_km: number | null;
  trade: CompanyTradeId | null;
  send_customer_confirmation: boolean;
  chat_share_phone: boolean;
  chat_share_email: boolean;
  email_delivery_provider: string;
  email_delivery_ready: boolean;
  email_delivery_sends_real_email: boolean;
  created_at: string;
}

export interface CompanySettingsUpdate {
  name?: string;
  email?: string;
  phone?: string | null;
  notification_email?: string | null;
  notification_min_urgency?: "high" | "medium" | "low";
  service_area_center?: string | null;
  service_radius_km?: number | null;
  trade?: CompanyTradeId | null;
  send_customer_confirmation?: boolean;
  chat_share_phone?: boolean;
  chat_share_email?: boolean;
}

export interface CurrentUser {
  id: string;
  company_id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  dev_reset_url?: string | null;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}

export type LeadSource = "website" | "test" | "phone";

export type ServiceAreaStatus =
  | "not_configured"
  | "unknown"
  | "in_range"
  | "out_of_range";

export interface Lead {
  id: string;
  company_id: string;
  conversation_id: string;
  source: LeadSource;
  is_first_website_inquiry: boolean;
  name: string;
  phone: string;
  email: string | null;
  company: string | null;
  location: string;
  postal_code: string | null;
  service_area_status: ServiceAreaStatus | null;
  service_area_distance_km: number | null;
  service_requested: string;
  description: string;
  urgency: string;
  preferred_callback_time: string;
  status: LeadStatus;
  summary: string | null;
  contactable: boolean;
  contact_method: ContactMethod | null;
  lead_score: number;
  qualification_status: QualificationStatus;
  inquiry_kind: InquiryKind;
  notification_sent_at: string | null;
  customer_confirmation_sent_at: string | null;
  appointment_confirmation_preference: AppointmentConfirmationPreference | null;
  appointment_confirmation_sent_at: string | null;
  contacted_at: string | null;
  archived_at: string | null;
  created_at: string;
}

export interface PaginatedLeads {
  items: Lead[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export type IntakeChannel =
  | "email"
  | "website"
  | "voice"
  | "whatsapp"
  | "manual";

export type IntakeStatus =
  | "received"
  | "processing"
  | "ready"
  | "needs_review"
  | "failed"
  | "exported"
  | "discarded";

export type IntakeUrgency = "high" | "medium" | "low" | "unknown";
export type IntakeKind = "appointment_consultation" | "quote" | "other";
export type IntakeScope = "in_scope" | "out_of_scope" | "unclear";
export type IntakeReviewDecision = "approve" | "save_for_review" | "discard";

export type IntakeRecommendedAction =
  | "call_immediately"
  | "schedule_visit"
  | "prepare_quote"
  | "request_missing_information"
  | "manual_route"
  | "discard_spam"
  | "merge_duplicate";

export interface IntakeServiceAddress {
  street: string | null;
  postal_code: string | null;
  city: string | null;
}

export interface IntakeAttachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  sha256: string;
  created_at: string;
}

export interface IntakeItem {
  id: string;
  company_id: string;
  channel: IntakeChannel;
  status: IntakeStatus;
  subject: string;
  sender_name: string | null;
  sender_email: string | null;
  received_at: string | null;
  customer_name: string | null;
  customer_company: string | null;
  customer_email: string | null;
  customer_phone: string | null;
  service_address: IntakeServiceAddress | null;
  service_requested: string | null;
  description: string | null;
  urgency: IntakeUrgency | null;
  preferred_time: string | null;
  inquiry_kind: IntakeKind | null;
  inquiry_scope: IntakeScope | null;
  contactable: boolean;
  needs_human_review: boolean;
  review_reasons: string[];
  recommended_action: IntakeRecommendedAction | null;
  field_confidence: Record<string, number>;
  safety_warning: string | null;
  processing_error: string | null;
  processing_attempts: number;
  processed_at: string | null;
  exported_at: string | null;
  duplicate_of_id: string | null;
  attachments: IntakeAttachment[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedIntakeItems {
  items: IntakeItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface IntakeSetup {
  email_enabled: boolean;
  inbound_email: string | null;
}

export interface IntakeReviewRequest {
  decision: IntakeReviewDecision;
  customer_name?: string | null;
  customer_company?: string | null;
  customer_email?: string | null;
  customer_phone?: string | null;
  service_address?: IntakeServiceAddress | null;
  service_requested?: string | null;
  description?: string | null;
  urgency?: IntakeUrgency | null;
  preferred_time?: string | null;
  inquiry_kind?: IntakeKind | null;
  inquiry_scope?: IntakeScope | null;
  recommended_action?: IntakeRecommendedAction | null;
}

export interface SeedDemoDataResponse {
  created: number;
  skipped: number;
  deleted?: number;
  lead_ids: string[];
  message: string;
}

export interface LeadExtractedData {
  name: string | null;
  phone: string | null;
  email: string | null;
  company: string | null;
  location: string | null;
  postal_code: string | null;
  service_requested: string | null;
  description: string | null;
  urgency: string | null;
  preferred_callback_time: string | null;
}

export interface LeadMessageRequest {
  conversation_id: string;
  message: string;
}

export interface LeadMessageResponse {
  reply: string;
  lead_complete: boolean;
  missing_fields: string[];
  extracted_data: LeadExtractedData;
  lead_id: string | null;
}

export const LEAD_STATUSES: LeadStatus[] = [
  "new",
  "contacted",
];
