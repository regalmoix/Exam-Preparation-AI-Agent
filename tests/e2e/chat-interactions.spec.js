import { test, expect } from '@playwright/test';

test.describe('Chat Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="app-container"]', { timeout: 10000 });
  });

  test('type in chat box and send message', async ({ page }) => {
    const chatInput = page.locator('[data-testid="chat-input"]').or(page.locator('input[placeholder*="message"]')).or(page.locator('textarea[placeholder*="message"]'));
    const sendButton = page.locator('[data-testid="send-button"]').or(page.locator('button:has-text("Send")'));

    // Type a test message
    const testMessage = 'What can you help me with?';
    await chatInput.fill(testMessage);

    // Verify message appears in input
    await expect(chatInput).toHaveValue(testMessage);

    // Send the message
    await sendButton.click();

    // Verify message appears in chat history
    await expect(page.locator('[data-testid="chat-messages"]').or(page.locator('[data-testid="message-list"]'))).toContainText(testMessage);

    // Verify input is cleared after sending
    await expect(chatInput).toHaveValue('');
  });

  test('receive response from chat', async ({ page }) => {
    const chatInput = page.locator('[data-testid="chat-input"]').or(page.locator('input[placeholder*="message"]')).or(page.locator('textarea[placeholder*="message"]'));
    const sendButton = page.locator('[data-testid="send-button"]').or(page.locator('button:has-text("Send")'));

    // Send a message
    await chatInput.fill('Hello, can you help me?');
    await sendButton.click();

    // Wait for response (look for assistant message)
    await expect(page.locator('[data-testid="assistant-message"]').or(page.locator('.message.assistant')).or(page.locator('[data-role="assistant"]'))).toBeVisible({ timeout: 30000 });

    // Verify response contains some content
    const responseText = await page.locator('[data-testid="assistant-message"]').or(page.locator('.message.assistant')).or(page.locator('[data-role="assistant"]')).first().textContent();
    expect(responseText.length).toBeGreaterThan(10);
  });

  test('send message with Enter key', async ({ page }) => {
    const chatInput = page.locator('[data-testid="chat-input"]').or(page.locator('input[placeholder*="message"]')).or(page.locator('textarea[placeholder*="message"]'));

    const testMessage = 'Testing Enter key functionality';
    await chatInput.fill(testMessage);

    // Press Enter to send message
    await chatInput.press('Enter');

    // Verify message appears in chat history
    await expect(page.locator('[data-testid="chat-messages"]').or(page.locator('[data-testid="message-list"]'))).toContainText(testMessage);
  });

  test('display chat interface elements', async ({ page }) => {
    // Verify chat input is present
    await expect(page.locator('[data-testid="chat-input"]').or(page.locator('input[placeholder*="message"]')).or(page.locator('textarea[placeholder*="message"]'))).toBeVisible();

    // Verify send button is present
    await expect(page.locator('[data-testid="send-button"]').or(page.locator('button:has-text("Send")'))).toBeVisible();

    // Verify chat messages area is present
    await expect(page.locator('[data-testid="chat-messages"]').or(page.locator('[data-testid="message-list"]'))).toBeVisible();
  });

  test('handle long message input', async ({ page }) => {
    const chatInput = page.locator('[data-testid="chat-input"]').or(page.locator('input[placeholder*="message"]')).or(page.locator('textarea[placeholder*="message"]'));
    const sendButton = page.locator('[data-testid="send-button"]').or(page.locator('button:has-text("Send")'));

    // Create a long message
    const longMessage = 'This is a very long message that tests how the chat interface handles lengthy input text. '.repeat(10);

    await chatInput.fill(longMessage);
    await sendButton.click();

    // Verify long message is handled properly
    await expect(page.locator('[data-testid="chat-messages"]').or(page.locator('[data-testid="message-list"]'))).toContainText(longMessage.substring(0, 100));
  });

  test('test specific queries for different intents', async ({ page }) => {
    const chatInput = page.locator('[data-testid="chat-input"]').or(page.locator('input[placeholder*="message"]')).or(page.locator('textarea[placeholder*="message"]'));
    const sendButton = page.locator('[data-testid="send-button"]').or(page.locator('button:has-text("Send")'));

    // Test summarization intent
    await chatInput.fill('Can you summarize the document I uploaded?');
    await sendButton.click();

    await expect(page.locator('[data-testid="assistant-message"]').or(page.locator('.message.assistant')).or(page.locator('[data-role="assistant"]'))).toBeVisible({ timeout: 30000 });

    // Test research intent
    await chatInput.fill('Research information about machine learning');
    await sendButton.click();

    // Wait for second response
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-testid="assistant-message"]').or(page.locator('.message.assistant')).or(page.locator('[data-role="assistant"]'))).toHaveCount(2, { timeout: 30000 });
  });
});