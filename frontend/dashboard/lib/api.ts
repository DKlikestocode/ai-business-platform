import { buildApiUrl } from "@/lib/api-config";
import { clearAccessToken, getAccessToken } from "@/lib/auth-storage";
import type { LeadSort } from "@/lib/lead-qualification";
import type { InquiryKindFilter } from "@/lib/inquiry-kind";
import { formatUserFacingError } from "@/lib/errors";
import type {
  Company,
  CompanyActivation,
  CompanyActivationUpdate,
  CompanyCreateRequest,
  CompanySettings,
  CompanySettingsUpdate,
  CurrentUser,
  Lead,
  LeadMessageRequest,
  LeadMessageResponse,
  LeadStatus,
  IntakeItem,
  IntakeReviewRequest,
  IntakeSetup,
  IntakeStatus,
  LoginRequest,
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  ResetPasswordRequest,
  PaginatedLeads,
  PaginatedIntakeItems,
  QualificationStatus,
  SeedDemoDataResponse,
  TokenResponse,
  UserCreateRequest,
  UserCreateResponse,
} from "@/lib/types";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

function formatErrorDetail(status: number, detail: string): string {
  if (status === 0) {
    return detail;
  }

  if (detail.includes("Missing credentials") || detail.includes("OPENAI_API_KEY")) {
    return "Backend is missing OPENAI_API_KEY. Add it to .env and restart the backend.";
  }

  if (detail.length > 300) {
    return `Request failed (${status}). Check backend logs for details.`;
  }

  return detail || `Request failed with status ${status}.`;
}

async function readErrorDetail(response: Response): Promise<string> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      const payload = (await response.json()) as { detail?: unknown };
      if (typeof payload.detail === "string") {
        return payload.detail;
      }
      if (Array.isArray(payload.detail)) {
        return JSON.stringify(payload.detail);
      }
    } catch {
      return response.statusText;
    }
  }

  return response.text();
}

function buildAuthHeaders(init?: RequestInit): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (init?.headers) {
    const extra =
      init.headers instanceof Headers
        ? Object.fromEntries(init.headers.entries())
        : Array.isArray(init.headers)
          ? Object.fromEntries(init.headers)
          : init.headers;
    Object.assign(headers, extra);
  }

  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = buildApiUrl(path);

  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: buildAuthHeaders(init),
      cache: "no-store",
      credentials: "same-origin",
    });
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Network error while contacting the API.";
    throw new ApiError(
      `Unable to reach the API at ${url || path}. ${message}`,
      0,
    );
  }

  if (response.status === 401) {
    const isAuthEndpoint =
      path.startsWith("/api/v1/auth/login") || path.startsWith("/api/auth/session");
    if (!isAuthEndpoint && unauthorizedHandler) {
      unauthorizedHandler();
    }
  }

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    const message = formatErrorDetail(response.status, detail);
    throw new ApiError(formatUserFacingError(new ApiError(message, response.status)), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function requestPasswordReset(
  payload: ForgotPasswordRequest,
): Promise<ForgotPasswordResponse | null> {
  const url = buildApiUrl("/api/v1/auth/forgot-password");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: buildAuthHeaders(),
      body: JSON.stringify(payload),
      cache: "no-store",
      credentials: "same-origin",
    });
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Network error while contacting the API.";
    throw new ApiError(
      `Unable to reach the API at ${url}. ${message}`,
      0,
    );
  }

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    const message = formatErrorDetail(response.status, detail);
    throw new ApiError(formatUserFacingError(new ApiError(message, response.status)), response.status);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json() as Promise<ForgotPasswordResponse>;
}

export async function resetPassword(payload: ResetPasswordRequest): Promise<void> {
  await request("/api/v1/auth/reset-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchCurrentUser(): Promise<CurrentUser> {
  return request<CurrentUser>("/api/v1/auth/me");
}

export async function establishSession(): Promise<void> {
  await request("/api/auth/session", { method: "POST" });
}

export async function clearSession(): Promise<void> {
  clearAccessToken();
  await request("/api/auth/session", { method: "DELETE" });
}

export async function fetchLeads(params?: {
  page?: number;
  page_size?: number;
  status?: LeadStatus | "";
  qualification_status?: QualificationStatus | "";
  contactable?: boolean | "";
  sort?: LeadSort;
  archived?: boolean;
  inquiry_kind?: InquiryKindFilter;
}): Promise<PaginatedLeads> {
  const search = new URLSearchParams();
  search.set("page", String(params?.page ?? 1));
  search.set("page_size", String(params?.page_size ?? 20));
  if (params?.archived) {
    search.set("archived", "true");
  }
  if (params?.status) {
    search.set("status", params.status);
  }
  if (params?.qualification_status) {
    search.set("qualification_status", params.qualification_status);
  }
  if (params?.contactable === true || params?.contactable === false) {
    search.set("contactable", String(params.contactable));
  }
  if (params?.sort) {
    search.set("sort", params.sort);
  }
  if (params?.inquiry_kind) {
    search.set("inquiry_kind", params.inquiry_kind);
  }
  return request<PaginatedLeads>(`/api/v1/leads?${search.toString()}`);
}

export async function fetchLead(leadId: string): Promise<Lead> {
  return request<Lead>(`/api/v1/leads/${leadId}`);
}

export async function fetchIntakeItems(params?: {
  page?: number;
  page_size?: number;
  status?: IntakeStatus | "";
}): Promise<PaginatedIntakeItems> {
  const search = new URLSearchParams();
  search.set("page", String(params?.page ?? 1));
  search.set("page_size", String(params?.page_size ?? 20));
  if (params?.status) {
    search.set("status", params.status);
  }
  return request<PaginatedIntakeItems>(
    `/api/v1/intake-items?${search.toString()}`,
  );
}

export async function fetchIntakeItem(itemId: string): Promise<IntakeItem> {
  return request<IntakeItem>(`/api/v1/intake-items/${itemId}`);
}

export async function fetchIntakeSetup(): Promise<IntakeSetup> {
  return request<IntakeSetup>("/api/v1/intake-items/setup");
}

export async function reviewIntakeItem(
  itemId: string,
  payload: IntakeReviewRequest,
): Promise<IntakeItem> {
  return request<IntakeItem>(`/api/v1/intake-items/${itemId}/review`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function retryIntakeItem(itemId: string): Promise<IntakeItem> {
  return request<IntakeItem>(`/api/v1/intake-items/${itemId}/retry`, {
    method: "POST",
  });
}

export async function downloadIntakeSource(itemId: string): Promise<void> {
  return downloadAuthenticatedFile(
    `/api/v1/intake-items/${itemId}/source.eml`,
    `anfrage-${itemId}.eml`,
  );
}

export async function downloadIntakeAttachment(
  itemId: string,
  attachmentId: string,
  filename: string,
): Promise<void> {
  return downloadAuthenticatedFile(
    `/api/v1/intake-items/${itemId}/attachments/${attachmentId}`,
    filename,
  );
}

export async function exportIntakeCsv(itemId: string): Promise<void> {
  return downloadAuthenticatedFile(
    `/api/v1/intake-items/${itemId}/export.csv`,
    `auftrag-${itemId}.csv`,
  );
}

async function downloadAuthenticatedFile(
  path: string,
  filename: string,
): Promise<void> {
  const url = buildApiUrl(path);
  const response = await fetch(url, {
    method: "GET",
    headers: buildAuthHeaders({ headers: { Accept: "*/*" } }),
    cache: "no-store",
    credentials: "same-origin",
  });

  if (response.status === 401 && unauthorizedHandler) {
    unauthorizedHandler();
  }
  if (!response.ok) {
    const detail = await readErrorDetail(response);
    const message = formatErrorDetail(response.status, detail);
    throw new ApiError(
      formatUserFacingError(new ApiError(message, response.status)),
      response.status,
    );
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

export async function downloadLeadCalendarIcs(leadId: string): Promise<void> {
  const url = buildApiUrl(`/api/v1/leads/${leadId}/calendar.ics`);
  const token = getAccessToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method: "GET",
    headers,
    cache: "no-store",
    credentials: "same-origin",
  });

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    const message = formatErrorDetail(response.status, detail);
    throw new ApiError(formatUserFacingError(new ApiError(message, response.status)), response.status);
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = `termin-${leadId}.ics`;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

export interface AppointmentConfirmationResult {
  sent: boolean;
  appointment_confirmation_sent_at: string | null;
}

export async function sendAppointmentConfirmation(
  leadId: string,
): Promise<AppointmentConfirmationResult> {
  return request<AppointmentConfirmationResult>(
    `/api/v1/leads/${leadId}/appointment-confirmation`,
    {
      method: "POST",
      body: JSON.stringify({ channel: "email" }),
    },
  );
}

export async function updateLeadStatus(
  leadId: string,
  status: LeadStatus,
): Promise<Lead> {
  return request<Lead>(`/api/v1/leads/${leadId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function restoreLead(leadId: string): Promise<Lead> {
  return request<Lead>(`/api/v1/leads/${leadId}/restore`, {
    method: "PATCH",
  });
}

export async function deleteLead(leadId: string): Promise<void> {
  await request<void>(`/api/v1/leads/${leadId}`, {
    method: "DELETE",
  });
}

export async function deleteAllContactedLeads(): Promise<{ deleted: number }> {
  return request<{ deleted: number }>("/api/v1/leads/contacted?contactable=true", {
    method: "DELETE",
  });
}

export async function seedDemoData(): Promise<SeedDemoDataResponse> {
  return request<SeedDemoDataResponse>("/api/v1/dev/seed-demo-data", {
    method: "POST",
  });
}

export async function registerCompany(
  payload: CompanyCreateRequest,
): Promise<Company> {
  return request<Company>("/api/v1/companies", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function registerUser(
  payload: UserCreateRequest,
): Promise<UserCreateResponse> {
  return request<UserCreateResponse>("/api/v1/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchCompany(companyId: string): Promise<Company> {
  return request<Company>(`/api/v1/companies/${companyId}`);
}

export async function fetchCompanySettings(): Promise<CompanySettings> {
  return request<CompanySettings>("/api/v1/company/settings");
}

export async function updateCompanySettings(
  payload: CompanySettingsUpdate,
): Promise<CompanySettings> {
  return request<CompanySettings>("/api/v1/company/settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function sendTestNotification(): Promise<void> {
  await request("/api/v1/company/settings/test-notification", {
    method: "POST",
  });
}

export interface TestVoiceIntakeResponse {
  reply: string;
  lead_id: string | null;
}

export async function sendTestVoiceIntake(): Promise<TestVoiceIntakeResponse> {
  return request<TestVoiceIntakeResponse>(
    "/api/v1/company/settings/test-voice-intake",
    {
      method: "POST",
    },
  );
}

export async function fetchCompanyActivation(): Promise<CompanyActivation> {
  return request<CompanyActivation>("/api/v1/company/activation");
}

export async function updateCompanyActivation(
  payload: CompanyActivationUpdate,
): Promise<CompanyActivation> {
  return request<CompanyActivation>("/api/v1/company/activation", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function sendLeadMessage(
  payload: LeadMessageRequest,
): Promise<LeadMessageResponse> {
  return request<LeadMessageResponse>("/api/v1/agents/lead/message", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export { ApiError };
