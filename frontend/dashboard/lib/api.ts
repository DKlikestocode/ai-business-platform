import { buildApiUrl } from "@/lib/api-config";
import { clearAccessToken, getAccessToken } from "@/lib/auth-storage";
import type { LeadSort } from "@/lib/lead-qualification";
import { formatUserFacingError } from "@/lib/errors";
import type {
  Company,
  CompanyCreateRequest,
  CompanySettings,
  CompanySettingsUpdate,
  CurrentUser,
  Lead,
  LeadMessageRequest,
  LeadMessageResponse,
  LeadStatus,
  LoginRequest,
  PaginatedLeads,
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
}): Promise<PaginatedLeads> {
  const search = new URLSearchParams();
  search.set("page", String(params?.page ?? 1));
  search.set("page_size", String(params?.page_size ?? 20));
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
  return request<PaginatedLeads>(`/api/v1/leads?${search.toString()}`);
}

export async function fetchLead(leadId: string): Promise<Lead> {
  return request<Lead>(`/api/v1/leads/${leadId}`);
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

export async function sendLeadMessage(
  payload: LeadMessageRequest,
): Promise<LeadMessageResponse> {
  return request<LeadMessageResponse>("/api/v1/agents/lead/message", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export { ApiError };
