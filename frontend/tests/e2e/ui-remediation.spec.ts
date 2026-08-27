import { expect, test, type Page } from "@playwright/test";

declare const Buffer: { from(value: string): never };

const documentItem = {
  document_id: "doc-1",
  name: "FLEXCUBE Operations Manual.pdf",
  file_type: "pdf",
  source_type: "flexcube_manual",
  status: "COMPLETED_WITH_WARNING",
  file_size_bytes: 1024 * 1024,
  chunks_indexed: 18,
  uploaded_at: "2026-08-27T10:00:00Z",
  updated_at: "2026-08-27T10:30:00Z",
};

const documentDetail = {
  ...documentItem,
  original_filename: documentItem.name,
  checksum: "a".repeat(64),
  description: null,
  chunks_created: 20,
  latest_job: {
    job_id: "job-1",
    status: "COMPLETED_WITH_WARNING",
    chunks_created: 20,
    chunks_indexed: 18,
    parse_warnings: [
      { element_type: "table", description: "One table could not be parsed", page_number: 12 },
    ],
  },
};

async function mockSessionAndDocuments(page: Page) {
  await page.route("**/api/v1/sessions", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({
          session_id: "session-1",
          created_at: "2026-08-27T10:00:00Z",
          expires_at: "2026-08-27T10:30:00Z",
        }),
      });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/v1/documents", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [documentItem], total: 1, limit: 20, next_cursor: null }),
      });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/v1/documents/doc-1", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(documentDetail) });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/v1/ingestion/jobs/job-1", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        job_id: "job-1",
        document_id: "doc-1",
        status: "COMPLETED_WITH_WARNING",
        attempt_count: 1,
        chunks_created: 20,
        chunks_indexed: 18,
        started_at: "2026-08-27T10:00:00Z",
        completed_at: "2026-08-27T10:30:00Z",
        last_error: null,
        parse_warnings: documentDetail.latest_job.parse_warnings,
      }),
    });
  });
  await page.route("**/api/v1/chat", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session_id: "session-1",
        question: "How do I use BA435?",
        answer_text: "Open the task and follow the documented procedure.",
        answer_type: "GROUNDED",
        citations: [{
          chunk_id: "chunk-1",
          document_id: "doc-1",
          document_name: documentItem.name,
          page_number: 142,
          section: "Task Codes > BA435",
          task_code: "BA435",
          screen_name: "Customer Account Screen",
          menu_path: null,
          prerequisites: [],
          modes: [],
          field_names: [],
          procedure_steps: [],
          error_code: null,
          jira_id: null,
          rca_reference: null,
          source_type: "flexcube_manual",
          relevance_score: 0.92,
        }],
        insufficient_information: false,
        model_used: null,
      }),
    });
  });
}

test.describe("UI remediation responsive checkpoints", () => {
  test("captures chat shell and mobile navigation at target sizes", async ({ page }, testInfo) => {
    await mockSessionAndDocuments(page);

    for (const viewport of [
      { width: 1280, height: 800 },
      { width: 1024, height: 768 },
      { width: 768, height: 1024 },
      { width: 375, height: 812 },
    ]) {
      await page.setViewportSize(viewport);
      await page.goto("/chat");
      await expect(page.getByRole("heading", { name: "Chat" })).toBeVisible();
      await expect(page.getByRole("textbox", { name: "Question" })).toBeVisible();
      await expect(page.getByRole("main")).toBeVisible();
      await page.screenshot({ path: testInfo.outputPath(`chat-${viewport.width}.png`), fullPage: true });
    }

    await page.getByRole("button", { name: "Menu" }).click();
    await expect(page.getByRole("navigation")).toBeVisible();
    await page.screenshot({ path: testInfo.outputPath("chat-mobile-navigation.png"), fullPage: true });
  });

  test("captures configuration table, warning, upload validation, citation, and dialog states", async ({ page }, testInfo) => {
    await mockSessionAndDocuments(page);
    await page.goto("/config/documents");
    await expect(page.getByRole("table", { name: "Knowledge documents" })).toBeVisible();
    await page.screenshot({ path: testInfo.outputPath("documents-table.png"), fullPage: true });

    await page.getByRole("button", { name: documentItem.name }).click();
    await expect(page.getByRole("heading", { name: documentItem.name })).toBeVisible();
    await expect(page.getByText("Content warnings (1)")).toBeVisible();
    await page.getByText("Content warnings (1)").click();
    await page.screenshot({ path: testInfo.outputPath("document-warning.png"), fullPage: true });

    await page.getByLabel("Source file").setInputFiles({ name: "unsupported.xlsx", mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", buffer: Buffer.from("data") });
    await expect(page.getByRole("alert")).toContainText("Supported formats");
    await page.screenshot({ path: testInfo.outputPath("upload-validation.png"), fullPage: true });

    await page.getByRole("button", { name: "Delete document" }).click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(page.getByRole("button", { name: "Cancel" })).toBeFocused();
    await page.screenshot({ path: testInfo.outputPath("delete-dialog.png"), fullPage: true });
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toBeHidden();
    await expect(page.getByRole("button", { name: "Delete document" })).toBeFocused();

    await page.goto("/chat");
    await page.getByRole("textbox", { name: "Question" }).fill("How do I use BA435?");
    await page.getByRole("button", { name: "Ask" }).click();
    await expect(page.getByRole("article", { name: "Support response" })).toBeVisible();
    await page.getByText(`Page 142`).first().click();
    await page.screenshot({ path: testInfo.outputPath("citation-expanded.png"), fullPage: true });
  });
});
