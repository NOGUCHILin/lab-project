import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';

// Load environment variables from .env.local
dotenv.config({ path: '.env.local' });

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3005',
    trace: 'on-first-retry',
    headless: true,
    // NixOS Chromiumパスを指定
    launchOptions: {
      executablePath: '/run/current-system/sw/bin/chromium',
    },
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Playwrightに同梱されたChromiumを使用
        // NixOS環境では自動ダウンロードされたブラウザを使う
      },
    },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: true,  // 既存のサーバーを使用
  },
});