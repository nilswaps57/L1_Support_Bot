import type { ApiError } from "./client";
import { isSafeDisplayedText, safeDisclosureFallback } from "../security/nonDisclosure";

export function safeApiError(status: number, responseBody?: unknown): ApiError {
  if (responseBody && typeof responseBody === "object") {
    const candidate = responseBody as Partial<ApiError>;
    const message = typeof candidate.message === "string" && isSafeDisplayedText(candidate.message)
      ? candidate.message
      : safeDisclosureFallback;
    return {
      error_code: typeof candidate.error_code === "string" ? candidate.error_code : "HTTP_ERROR",
      message,
      request_id: typeof candidate.request_id === "string" ? candidate.request_id : "unknown",
      timestamp: typeof candidate.timestamp === "string" ? candidate.timestamp : new Date().toISOString(),
      details: {},
    };
  }
  return {
    error_code: status >= 500 ? "SERVICE_UNAVAILABLE" : "HTTP_ERROR",
    message: status >= 500
      ? "The requested service is temporarily unavailable."
      : "The request could not be completed.",
    request_id: "unknown",
    timestamp: new Date().toISOString(),
    details: {},
  };
}
