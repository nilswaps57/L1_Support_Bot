const unsafeTextPatterns = [
  /\b(?:system|developer|hidden|original)\s+(?:prompt|instructions?)\b/i,
  /\b(?:api\s*key|access\s*token|bearer\s+token|client\s+secret|password|credentials?)\s*[:=]/i,
  /\b(?:DATABASE_URL|QDRANT_URL|OLLAMA_|EMBEDDING_|CORS_ALLOWED_ORIGINS)\w*\s*=/i,
  /(?:^|\s)\/(?:home|srv|app|etc|var|tmp|workspace)\/\S+/i,
  /\b(?:Traceback \(most recent call last\):|File "[^"]+", line \d+)/i,
  /\b(?:select|insert|update|delete|drop|alter)\b.{0,120}\b(?:from|into|table|where)\b/i,
  /(?:^|\n)\s*(?:sudo\s+|curl\s+https?:\/\/|wget\s+https?:\/\/|rm\s+-rf\s+)/i,
];

export const safeDisclosureFallback =
  "The response cannot include internal details. Please ask about documented FLEXCUBE support content.";

export function isSafeDisplayedText(text: string): boolean {
  return !unsafeTextPatterns.some((pattern) => pattern.test(text));
}

export function safeDisplayedText(text: string): string {
  return isSafeDisplayedText(text) ? text : safeDisclosureFallback;
}
