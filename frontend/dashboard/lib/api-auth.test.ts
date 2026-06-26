import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiError,
  fetchCompanyActivation,
  fetchCompanySettings,
  fetchCurrentUser,
  fetchLeads,
  login,
  setUnauthorizedHandler,
  updateCompanySettings,
} from "@/lib/api";
import { clearAccessToken, setAccessToken } from "@/lib/auth-storage";

class MemoryStorage {
  private store = new Map<string, string>();

  getItem(key: string): string | null {
    return this.store.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.store.set(key, value);
  }

  removeItem(key: string): void {
    this.store.delete(key);
  }
}

describe("api auth client", () => {
  beforeEach(() => {
    const storage = new MemoryStorage();
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: { sessionStorage: storage },
    });
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    clearAccessToken();
    setUnauthorizedHandler(null);
    vi.unstubAllGlobals();
  });

  it("sends login credentials without an authorization header", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          access_token: "token-123",
          token_type: "bearer",
          expires_in: 1800,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    const response = await login({
      email: "user@example.com",
      password: "secure-password",
    });

    expect(response.access_token).toBe("token-123");
    const [, init] = fetchMock.mock.calls[0];
    const headers = init?.headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it("attaches the bearer token to authenticated requests", async () => {
    setAccessToken("stored-token");
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          id: "user-1",
          company_id: "company-1",
          first_name: "Jane",
          last_name: "Doe",
          email: "user@example.com",
          role: "member",
          is_active: true,
          created_at: "2026-06-10T12:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    const user = await fetchCurrentUser();

    expect(user.email).toBe("user@example.com");
    const [, init] = fetchMock.mock.calls[0];
    const headers = init?.headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer stored-token");
  });

  it("passes qualification filters and sort params when listing leads", async () => {
    setAccessToken("stored-token");
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          items: [],
          page: 1,
          page_size: 20,
          total: 0,
          total_pages: 0,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await fetchLeads({
      qualification_status: "contactable",
      contactable: true,
      sort: "urgency_desc",
    });

    const [url] = fetchMock.mock.calls[0];
    expect(String(url)).toContain("qualification_status=contactable");
    expect(String(url)).toContain("contactable=true");
    expect(String(url)).toContain("sort=urgency_desc");
  });

  it("loads and updates company settings with bearer auth", async () => {
    setAccessToken("stored-token");
    const fetchMock = vi.mocked(fetch);
    const settingsPayload = {
      name: "Acme Co",
      slug: "acme-co",
      email: "hello@acme.co",
      phone: null,
      notification_email: null,
      notification_min_urgency: "medium" as const,
      service_area_center: null,
      service_radius_km: null,
      email_delivery_provider: "logging",
      email_delivery_ready: true,
      email_delivery_sends_real_email: false,
      created_at: "2026-06-10T12:00:00Z",
    };

    fetchMock
      .mockResolvedValueOnce(
        new Response(JSON.stringify(settingsPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            ...settingsPayload,
            name: "Acme Plumbing",
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          },
        ),
      );

    const settings = await fetchCompanySettings();
    expect(settings.slug).toBe("acme-co");

    const updated = await updateCompanySettings({ name: "Acme Plumbing" });
    expect(updated.name).toBe("Acme Plumbing");

    const patchCall = fetchMock.mock.calls[1];
    expect(patchCall[0]).toContain("/api/v1/company/settings");
    expect(patchCall[1]?.method).toBe("PATCH");
    const patchHeaders = patchCall[1]?.headers as Record<string, string>;
    expect(patchHeaders.Authorization).toBe("Bearer stored-token");
  });

  it("fetches company activation with bearer auth", async () => {
    setAccessToken("stored-token");
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          status: "awaiting_widget",
          notification_configured: false,
          website_url: null,
          widget_live_at: null,
          widget_last_seen_at: null,
          widget_last_origin: null,
          first_website_inquiry_at: null,
          install: {
            company_slug: "acme-co",
            embed_snippet:
              '<div data-install-token="secret"></div>',
          },
          updated_at: "2026-06-10T12:00:00Z",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    const activation = await fetchCompanyActivation();

    expect(activation.status).toBe("awaiting_widget");
    expect(activation.install.embed_snippet).toContain("data-install-token=");
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain("/api/v1/company/activation");
    const headers = init?.headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer stored-token");
  });

  it("invokes the unauthorized handler on 401 responses", async () => {
    setAccessToken("expired-token");
    const fetchMock = vi.mocked(fetch);
    const unauthorized = vi.fn();
    setUnauthorizedHandler(unauthorized);

    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Invalid access token." }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(fetchCurrentUser()).rejects.toBeInstanceOf(ApiError);
    expect(unauthorized).toHaveBeenCalledTimes(1);
  });
});
