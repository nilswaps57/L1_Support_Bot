import { useQuery } from "@tanstack/react-query";

import { getHealth, type HealthResponse } from "../api/health";

export function useRuntimeHealth() {
  return useQuery<HealthResponse>({
    queryKey: ["runtime-health"],
    queryFn: getHealth,
    retry: false,
    refetchInterval: 30_000,
    staleTime: 10_000,
  });
}
