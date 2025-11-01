import { test, expect } from '@playwright/test';
import { join } from 'path';

test.describe('File Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="app-container"]', { timeout: 10000 });
  });

  test('upload file successfully', async ({ page }) => {
    const fileUploadInput = page.locator('input[type="file"]');

    const testFilePath = join(process.cwd(), 'tests/fixtures/sample.txt');
    await fileUploadInput.setInputFiles(testFilePath);

    // Wait for upload success indication
    await expect(page.locator('text=uploaded successfully')).toBeVisible({ timeout: 30000 });

    // Verify file appears in documents list
    await expect(page.locator('[data-testid="document-list"]')).toContainText('sample.txt');
  });

  test('delete file successfully', async ({ page }) => {
    // First upload a file
    const fileUploadInput = page.locator('input[type="file"]');
    const testFilePath = join(process.cwd(), 'tests/fixtures/sample.txt');
    await fileUploadInput.setInputFiles(testFilePath);

    await expect(page.locator('text=uploaded successfully')).toBeVisible({ timeout: 30000 });

    // Find and click delete button for the uploaded file
    const deleteButton = page.locator('[data-testid="delete-file-btn"]').first();
    await deleteButton.click();

    // Confirm deletion if there's a confirmation dialog
    const confirmButton = page.locator('button:has-text("Delete")').or(page.locator('button:has-text("Confirm")'));
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }

    // Wait for file to be removed from list
    await expect(page.locator('[data-testid="document-list"]')).not.toContainText('sample.txt', { timeout: 10000 });
  });

  test('display upload error for invalid file type', async ({ page }) => {
    const fileUploadInput = page.locator('input[type="file"]');

    // Try to upload an invalid file type
    const invalidFilePath = join(process.cwd(), 'tests/fixtures/invalid.exe');
    await fileUploadInput.setInputFiles(invalidFilePath);

    // Verify error message appears
    await expect(page.locator('text=not supported').or(page.locator('text=invalid'))).toBeVisible({ timeout: 10000 });
  });

  test('show documents list on page load', async ({ page }) => {
    // Check that documents list is visible
    await expect(page.locator('[data-testid="document-list"]')).toBeVisible();

    // Check for documents header or empty state
    const hasDocuments = await page.locator('[data-testid="document-item"]').count() > 0;
    const hasEmptyState = await page.locator('text=No documents').or(page.locator('text=Upload your first')).isVisible();

    expect(hasDocuments || hasEmptyState).toBe(true);
  });
});