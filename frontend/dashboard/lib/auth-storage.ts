const ACCESS_TOKEN_KEY = "ai-agent-platform:access-token";

function getStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.sessionStorage;
}

export function getAccessToken(): string | null {
  return getStorage()?.getItem(ACCESS_TOKEN_KEY) ?? null;
}

export function setAccessToken(token: string): void {
  getStorage()?.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  getStorage()?.removeItem(ACCESS_TOKEN_KEY);
}

export function hasAccessToken(): boolean {
  return Boolean(getAccessToken());
}
