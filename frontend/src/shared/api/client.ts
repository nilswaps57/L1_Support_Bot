import { safeApiError } from "./error-handler";

export type ApiError = {
  error_code: string;
  message: string;
  request_id: string;
  timestamp: string;
  details: Record<string, unknown>;
};

export class ApiClientError extends Error {
  readonly payload: ApiError;
  readonly status: number;

  constructor(status: number, payload: ApiError) {
    super(payload.message);
    this.name = "ApiClientError";
    this.status = status;
    this.payload = payload;
  }
}

export class ApiClient {
  constructor(private readonly baseUrl: string = "http://localhost:8000/api/v1") {}

  async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...init?.headers,
      },
    });

    if (!response.ok) {
      let responseBody: unknown;
      try {
        responseBody = await response.json();
      } catch {
        responseBody = undefined;
      }
      const payload = safeApiError(response.status, responseBody);
      throw new ApiClientError(response.status, payload);
    }

    if (response.status === 204) {
      return undefined as T;
    }
    return (await response.json()) as T;
  }
}

export const apiClient = new ApiClient();