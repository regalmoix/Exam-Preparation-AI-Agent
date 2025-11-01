import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5172',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: process.env.CI ? undefined : [
    {
      command: 'npm run dev',
      cwd: './frontend',
      port: 5172,
      reuseExistingServer: true,
      timeout: 120 * 1000,
    },
    {
      command: 'npm run backend',
      port: 8002,
      reuseExistingServer: true,
      timeout: 120 * 1000,
    }
  ],
});