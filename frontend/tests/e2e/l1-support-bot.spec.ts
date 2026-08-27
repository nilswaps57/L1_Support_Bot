import { expect, test, type Page } from "@playwright/test";

declare const Buffer: { from(value: string): never };

const documentItem = {
  document_id: "doc-e2e", name: "Reviewed FLEXCUBE manual.pdf", file_type: "pdf",
  source_type: "flexcube_manual", status: "COMPLETED", file_size_bytes: 1024,
  chunks_indexed: 12, uploaded_at: "2026-08-27T00:00:00Z", updated_at: "2026-08-27T00:00:00Z",
};

async function mockFlow(page: Page) {
  const workflowState = { status: "QUEUED", pollCount: 0, deleted: false };
  await page.route("**/api/v1/health", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "healthy", capabilities: { document_management: true, configuration_mutations: true } }) });
  });
  await page.route("**/api/v1/sessions", async (route) => {
    await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ session_id: "session-e2e", created_at: "2026-08-27T00:00:00Z", expires_at: "2026-08-27T01:00:00Z" }) });
  });
  await page.route("**/api/v1/documents", async (route) => {
    const items = workflowState.deleted ? [] : [{ ...documentItem, status: workflowState.status }];
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items, total: items.length, limit: 20, next_cursor: null }) });
  });
  await page.route("**/api/v1/documents/upload", async (route) => {
    workflowState.deleted = false;
    workflowState.status = "QUEUED";
    workflowState.pollCount = 0;
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ document_id: documentItem.document_id, job_id: "job-e2e", status: "QUEUED", name: documentItem.name, file_type: "pdf", file_size_bytes: 1024, checksum: "a".repeat(64) }) });
  });
  await page.route("**/api/v1/documents/doc-e2e", async (route) => {
    if (route.request().method() === "DELETE") {
      workflowState.deleted = true;
      workflowState.status = "DELETING";
      await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ document_id: documentItem.document_id, status: "DELETING" }) });
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ ...documentItem, status: workflowState.status, original_filename: documentItem.name, checksum: "a".repeat(64), description: null, chunks_created: workflowState.status === "QUEUED" ? 0 : 12, latest_job: { job_id: "job-e2e", status: workflowState.status, chunks_created: workflowState.status === "QUEUED" ? 0 : 12, chunks_indexed: workflowState.status === "QUEUED" ? 0 : 12, parse_warnings: [] } }) });
  });
  await page.route("**/api/v1/ingestion/jobs/job-e2e", async (route) => {
    const status = workflowState.pollCount++ === 0 ? "QUEUED" : "COMPLETED";
    workflowState.status = status;
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ job_id: "job-e2e", document_id: documentItem.document_id, status, attempt_count: 1, chunks_created: status === "QUEUED" ? 0 : 12, chunks_indexed: status === "QUEUED" ? 0 : 12, started_at: "2026-08-27T00:00:00Z", completed_at: status === "QUEUED" ? null : "2026-08-27T00:01:00Z", last_error: null, parse_warnings: [] }) });
  });
  await page.route("**/api/v1/chat", async (route) => {
    const response = workflowState.deleted
      ? { answer_id: "answer-e2e-deleted", session_id: "session-e2e", question: "What is BA435?", answer_text: "The available knowledge sources do not contain sufficient information to answer this question.", answer_type: "INSUFFICIENT", insufficient_information: true, model_used: null, citations: [] }
      : { answer_id: "answer-e2e", session_id: "session-e2e", question: "What is BA435?", answer_text: "The reviewed manual documents BA435.", answer_type: "GROUNDED", insufficient_information: false, model_used: "test", citations: [{ chunk_id: "chunk-e2e", document_id: documentItem.document_id, document_name: documentItem.name, page_number: 4, section: "BA435", task_code: "BA435", screen_name: null, menu_path: null, prerequisites: [], modes: [], field_names: [], procedure_steps: [], error_code: null, jira_id: null, rca_reference: null, source_type: "flexcube_manual", relevance_score: 0.9 }] };
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(response) });
  });
  await page.route("**/api/v1/feedback", async (route) => {
    await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ feedback_id: "feedback-e2e" }) });
  });
}

test("covers upload, indexed chat, citation, feedback, and delete", async ({ page }) => {
  await mockFlow(page);
  await page.goto("/config/documents");
  await page.getByLabel("Source file").setInputFiles({ name: "manual.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-1.4") });
  await page.getByRole("button", { name: "Upload" }).click();
  await expect(page.getByText("Reviewed FLEXCUBE manual.pdf is queued for processing.")).toBeVisible();

  await page.getByRole("button", { name: documentItem.name }).click();
  await expect(page.getByRole("article").getByRole("status")).toContainText("Queued");
  await expect(page.getByText("Ready", { exact: true })).toBeVisible({ timeout: 7000 });

  await page.goto("/chat");
  await page.getByRole("textbox", { name: "Question" }).fill("What is BA435?");
  await page.getByRole("button", { name: "Ask" }).click();
  const response = page.getByRole("article", { name: "Support response" });
  await expect(response).toBeVisible();
  await expect(page.getByRole("region", { name: "Conversation", exact: true })).toContainText("The reviewed manual documents BA435.");
  await expect(page.getByRole("region", { name: "Sources (1)" })).toBeVisible();
  await expect(page.getByText("BA435").first()).toBeVisible();
  await page.getByRole("button", { name: "Helpful", exact: true }).click();
  await page.getByRole("button", { name: "Send feedback" }).click();
  await expect(page.getByText("Feedback received. Thank you.")).toBeVisible();

  await page.goto("/config/documents");
  await page.getByRole("button", { name: documentItem.name }).click();
  await page.getByRole("button", { name: "Delete document" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Delete" }).click();
  await expect(page.getByRole("status")).toContainText("Document deleted");
  await page.goto("/config/documents");
  await expect(page.getByText("No documents yet")).toBeVisible();

  await page.goto("/chat");
  await page.getByRole("textbox", { name: "Question" }).fill("What is BA435?");
  await page.getByRole("button", { name: "Ask" }).click();
  await expect(page.getByRole("status")).toContainText("Insufficient information");
  await expect(page.getByText(documentItem.name)).toHaveCount(0);
  await expect(page.getByRole("region", { name: /Sources/ })).toHaveCount(0);
});
