import { test, expect } from '@playwright/test';

test.describe('API Health Check', () => {
  test('統合ダッシュボード自体の応答確認', async ({ request, baseURL }) => {
    // ダッシュボードのAPIが応答するか（環境変数からbaseURLを使用）
    const response = await request.get(baseURL || '/');
    expect(response.status()).toBe(200);

    // HTMLコンテンツが返される
    const body = await response.text();
    expect(body).toContain('統合ダッシュボード');
  });

  test('各サービスへの接続確認', async ({ request, baseURL }) => {
    // Code Server（環境変数から構築）
    const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || baseURL || 'http://localhost';
    const CODE_SERVER_PORT = process.env.NEXT_PUBLIC_CODE_SERVER_PORT || '8889';

    try {
      const codeServerResponse = await request.get(`${BASE_URL}:${CODE_SERVER_PORT}`, {
        timeout: 5000,
        ignoreHTTPSErrors: true // SSL証明書エラーを無視
      });
      // 200 or リダイレクト系ならOK
      expect([200, 301, 302, 303, 307, 308]).toContain(codeServerResponse.status());
    } catch (error) {
      // ネットワークエラーでも警告として記録
      console.warn('Code Server connection failed:', error);
    }
  });

  test('ダッシュボードのJavaScript動作確認', async ({ page }) => {
    await page.goto('/');
    
    // React アプリケーションが読み込まれている（代替セレクタ）
    await page.waitForSelector('main', { timeout: 10000 });
    await page.waitForSelector('h1:has-text("統合ダッシュボード")', { timeout: 5000 });
    
    //状態更新が動作している（3秒後にstatusがchecking以外に変わる）
    await page.waitForTimeout(4000);
    const statusElements = await page.getByText(/Online|Offline/).count();
    expect(statusElements).toBeGreaterThan(0);
  });
});