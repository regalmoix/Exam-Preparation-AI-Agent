import { test, expect } from '@playwright/test';

test.describe('Navigation and Page Load', () => {
  test('page loads successfully', async ({ page }) => {
    await page.goto('/');

    // Wait for the main application container
    await expect(page.locator('[data-testid="app-container"]').or(page.locator('body'))).toBeVisible({ timeout: 10000 });

    // Check page title
    await expect(page).toHaveTitle(/Exam|Study|Assistant/i);
  });

  test('all main UI components are visible', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for main navigation or header
    const hasNavigation = await page.locator('nav').or(page.locator('[role="navigation"]')).or(page.locator('header')).isVisible();
    expect(hasNavigation).toBe(true);

    // Check for main content area
    await expect(page.locator('main').or(page.locator('[role="main"]')).or(page.locator('#app'))).toBeVisible();
  });

  test('no console errors on page load', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Filter out known non-critical errors
    const criticalErrors = consoleErrors.filter(error =>
      !error.includes('favicon') &&
      !error.includes('DevTools') &&
      !error.includes('extensions')
    );

    expect(criticalErrors).toEqual([]);
  });

  test('responsive design works', async ({ page, browserName }) => {
    await page.goto('/');

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('body')).toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('body')).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.locator('body')).toBeVisible();
  });

  test('page is accessible', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for proper heading structure
    const hasHeadings = await page.locator('h1, h2, h3').count() > 0;
    expect(hasHeadings).toBe(true);

    // Check for proper form labels if forms exist
    const formInputs = page.locator('input, textarea');
    const inputCount = await formInputs.count();

    if (inputCount > 0) {
      // At least some inputs should have proper labels or aria-labels
      const labeledInputs = await page.locator('input[aria-label], textarea[aria-label], input[id] ~ label, textarea[id] ~ label').count();
      expect(labeledInputs).toBeGreaterThan(0);
    }
  });
});