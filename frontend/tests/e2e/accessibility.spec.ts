import { expect, test, type Page } from "@playwright/test";

declare const Buffer: { from(value: string): never };

const healthy = {
  status: "healthy",
  capabilities: {
    configuration_mutations: true,
    document_management: true,
  },
};

const configs = {
  llm: {
    provider: "ollama", model: "qwen2.5:0.5b", temperature: 0.1, max_tokens: 512,
    context_window: 4096, timeout_seconds: 30, max_retries: 2, label: null,
    api_key_configured: false, status: "ready",
  },
  embedding: {
    provider: "ollama", model: "nomic-embed-text", model_version: "latest", dimensions: 768,
    distance_method: "cosine", index_compatible: true, batch_size: 32, timeout_seconds: 30,
    label: null, api_key_configured: false, status: "ready",
  },
  retrieval: {
    top_k_candidates: 20, final_top_k: 5, similarity_threshold: 0.4, dense_weight: 0.7,
    sparse_weight: 0.3, rerank_enabled: false, rerank_top_k: 20, exact_id_boost: true,
    min_evidence_tokens: 100, status: "ready",
  },
  chunking: {
    strategy: "SEMANTIC_STRUCTURE", target_chunk_tokens: 512, min_chunk_tokens: 64,
    max_chunk_tokens: 1024, overlap_tokens: 64, table_as_unit: true,
    procedure_grouping: true, status: "ready",
  },
};

async function mockBaseApis(page: Page) {
  await page.route("**/api/v1/health", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(healthy) });
  });
  await page.route("**/api/v1/sessions", async (route) => {
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({ session_id: "accessibility-session", created_at: "2026-08-27T00:00:00Z", expires_at: "2026-08-27T01:00:00Z" }),
    });
  });
  await page.route("**/api/v1/documents", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], total: 0, limit: 20, next_cursor: null }) });
  });
  for (const [name, value] of Object.entries(configs)) {
    await page.route(`**/api/v1/config/${name}`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(value) });
    });
  }
}

test.describe("accessibility readiness", () => {
  test("chat and documents expose landmarks, labels, and keyboard focus", async ({ page }) => {
    await mockBaseApis(page);
    await page.goto("/chat");
    await expect(page.getByRole("main")).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Question" })).toBeVisible();
    await page.keyboard.press("Tab");
    await expect(page.locator(":focus")).toBeVisible();

    await page.goto("/config/documents");
    await expect(page.getByRole("heading", { name: "Upload document" })).toBeVisible();
    await expect(page.getByLabel("Source file")).toBeVisible();
    await expect(page.getByText("No documents yet")).toBeVisible();
  });

  test("configuration forms expose labelled controls and keyboard access", async ({ page }) => {
    await mockBaseApis(page);
    await page.goto("/config/ai");
    await expect(page.getByRole("heading", { name: "AI configuration" })).toBeVisible();
    await expect(page.getByLabel("Provider").first()).toBeVisible();
    await expect(page.getByLabel("Model").first()).toBeVisible();
    await page.keyboard.press("Tab");
    await expect(page.locator(":focus")).toBeVisible();
  });

  test("loading and error states remain announced", async ({ page }) => {
    await page.route("**/api/v1/health", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(healthy) });
    });
    await page.route("**/api/v1/config/**", async (route) => {
      await route.abort("failed");
    });
    await page.goto("/config/ai");
    await expect(page.getByRole("alert")).toContainText("temporarily unavailable");
  });

  test("responsive reflow keeps the main workflow visible at target widths", async ({ page }) => {
    await mockBaseApis(page);
    for (const viewport of [{ width: 1280, height: 800 }, { width: 768, height: 1024 }, { width: 375, height: 812 }]) {
      await page.setViewportSize(viewport);
      await page.goto("/chat");
      await expect(page.getByRole("main")).toBeVisible();
      await expect(page.getByRole("textbox", { name: "Question" })).toBeVisible();
      await expect(page.locator("body")).toHaveCSS("overflow-x", "visible");
    }
  });

  test("navigation exposes current state and mobile disclosure semantics", async ({ page }) => {
    await mockBaseApis(page);
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/chat");
    await expect(page.getByRole("link", { name: "Chat", exact: true })).toHaveAttribute("aria-current", "page");

    const menu = page.getByRole("button", { name: "Menu" });
    await expect(menu).toHaveAttribute("aria-expanded", "false");
    await menu.click();
    await expect(menu).toHaveAttribute("aria-expanded", "true");
    await expect(page.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
  });

  test("citations expose expandable source details with a stable heading structure", async ({ page }) => {
    await mockBaseApis(page);
    await page.route("**/api/v1/chat", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          answer_id: "answer-accessibility",
          session_id: "accessibility-session",
          question: "What is BA435?",
          answer_text: "BA435 opens the synthetic customer account screen.",
          answer_type: "GROUNDED",
          citations: [{
            chunk_id: "chunk-accessibility",
            document_id: "doc-accessibility",
            document_name: "Synthetic FLEXCUBE Guide",
            page_number: 42,
            section: "Synthetic task codes",
            task_code: "BA435",
            screen_name: "Customer account",
            menu_path: null,
            prerequisites: [],
            modes: [],
            field_names: [],
            procedure_steps: [],
            error_code: null,
            jira_id: null,
            rca_reference: null,
            source_type: "synthetic",
            relevance_score: 0.9,
          }],
          insufficient_information: false,
          model_used: "deterministic-fake",
        }),
      });
    });
    await page.goto("/chat");
    await page.getByRole("textbox", { name: "Question" }).fill("What is BA435?");
    await page.getByRole("button", { name: "Ask" }).click();
    await expect(page.getByRole("heading", { name: "Sources (1)" })).toBeVisible();
    await page.getByText("Synthetic FLEXCUBE Guide").click();
    await expect(page.getByText("Page", { exact: true })).toBeVisible();
    await expect(page.getByText("Task: BA435", { exact: true })).toBeVisible();
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page.locator("h3")).toHaveCount(0);
  });

  test("destructive dialog has an accessible name, traps focus, and closes on Escape", async ({ page }) => {
    await mockBaseApis(page);
    await page.route("**/api/v1/documents", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          items: [{
            document_id: "doc-1",
            name: "Synthetic guide",
            file_type: "md",
            source_type: "flexcube_manual",
            status: "COMPLETED",
            file_size_bytes: 100,
            chunks_indexed: 4,
            uploaded_at: "2026-08-27T00:00:00Z",
            updated_at: "2026-08-27T00:00:00Z",
          }],
          total: 1,
          limit: 20,
          next_cursor: null,
        }),
      });
    });
    await page.route("**/api/v1/documents/doc-1", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          document_id: "doc-1",
          name: "Synthetic guide",
          original_filename: "guide.md",
          status: "COMPLETED",
          chunks_created: 4,
          chunks_indexed: 4,
          latest_job: null,
        }),
      });
    });
    await page.goto("/config/documents");
    await page.getByRole("button", { name: "Synthetic guide", exact: true }).click();
    await page.getByRole("button", { name: "Delete document" }).click();
    const dialog = page.getByRole("dialog", { name: "Delete Synthetic guide?" });
    await expect(dialog).toBeVisible();
    await expect(page.getByRole("button", { name: "Cancel" })).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(page.getByRole("button", { name: "Confirm delete" })).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(page.getByRole("button", { name: "Cancel" })).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(page.getByRole("button", { name: "Delete document" })).toBeFocused();
  });
});
