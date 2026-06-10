import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/api";
import { formatUserFacingError } from "@/lib/errors";

describe("formatUserFacingError", () => {
  it("maps session errors to a friendly message", () => {
    expect(
      formatUserFacingError(new ApiError("Invalid access token.", 401)),
    ).toContain("session expired");
  });

  it("maps duplicate email errors clearly", () => {
    expect(
      formatUserFacingError(
        new Error("User with email 'a@b.com' already exists."),
      ),
    ).toContain("already exists");
  });
});
