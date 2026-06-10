import { afterEach, describe, expect, it } from "vitest";

import {
  clearAccessToken,
  getAccessToken,
  hasAccessToken,
  setAccessToken,
} from "@/lib/auth-storage";

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

describe("auth-storage", () => {
  afterEach(() => {
    clearAccessToken();
  });

  it("returns null when no token is stored", () => {
    const storage = new MemoryStorage();
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: { sessionStorage: storage },
    });

    expect(getAccessToken()).toBeNull();
    expect(hasAccessToken()).toBe(false);
  });

  it("stores and retrieves the access token", () => {
    const storage = new MemoryStorage();
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: { sessionStorage: storage },
    });

    setAccessToken("jwt-token-value");

    expect(getAccessToken()).toBe("jwt-token-value");
    expect(hasAccessToken()).toBe(true);
  });

  it("clears the stored access token", () => {
    const storage = new MemoryStorage();
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: { sessionStorage: storage },
    });

    setAccessToken("jwt-token-value");
    clearAccessToken();

    expect(getAccessToken()).toBeNull();
    expect(hasAccessToken()).toBe(false);
  });
});
