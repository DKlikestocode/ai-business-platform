export interface UserFacingErrorMessages {
  openai?: string;
  session?: string;
  network?: string;
  duplicateEmail?: string;
}

export function formatUserFacingError(
  error: unknown,
  fallback = "Something went wrong. Please try again.",
  messages?: UserFacingErrorMessages,
): string {
  if (error instanceof Error) {
    const message = error.message.trim();
    if (!message) {
      return fallback;
    }

    if (message.includes("OPENAI_API_KEY")) {
      return (
        messages?.openai ??
        "The AI assistant is not configured yet. Ask your administrator to set OPENAI_API_KEY."
      );
    }

    if (
      message.includes("Not authenticated") ||
      message.includes("Invalid access token")
    ) {
      return messages?.session ?? "Your session expired. Please sign in again.";
    }

    if (message.includes("Unable to reach the API")) {
      return (
        messages?.network ??
        "We could not reach the server. Check your connection and try again."
      );
    }

    if (message.includes("User with email") && message.includes("already exists")) {
      return (
        messages?.duplicateEmail ??
        "An account with this email already exists. Try signing in instead."
      );
    }

    if (message.length > 220) {
      return fallback;
    }

    return message;
  }

  return fallback;
}
