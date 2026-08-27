import { ErrorBoundary } from "../shared/components/ErrorBoundary";
import { AppRouter } from "./router";
import { Providers } from "./providers";

export function App() {
  return (
    <Providers>
      <ErrorBoundary>
        <AppRouter />
      </ErrorBoundary>
    </Providers>
  );
}