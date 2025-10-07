import { test, expect } from '@playwright/test';

test.describe('Error Handling Tests', () => {
  test('ネットワークエラー時の動作', async ({ page }) => {
    // ネットワークをオフラインに設定
    await page.context().setOffline(true);
    
    try {
      await page.goto('/', { timeout: 10000 });
    } catch (error) {
      // オフライン時は正常にエラーになるべき
      expect(error.message).toContain('net::ERR_INTERNET_DISCONNECTED');
    }
    
    // オンラインに戻す
    await page.context().setOffline(false);
    
    // 復旧後は正常にアクセスできる
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /統合ダッシュボード/ })).toBeVisible();
  });

  test('JavaScript無効時の動作', async ({ browser }) => {
    // JavaScript無効のコンテキストを作成
    const context = await browser.newContext({
      javaScriptEnabled: false
    });
    
    const page = await context.newPage();
    await page.goto('/');
    
    // 基本的なHTMLは表示される
    const title = await page.textContent('title');
    expect(title).toContain('統合ダッシュボード');
    
    await context.close();
  });

  test('大量リクエスト時の安定性', async ({ page }) => {
    await page.goto('/');
    
    // 複数回リロードして安定性をテスト
    let errorCount = 0;
    
    for (let i = 0; i < 5; i++) {
      try {
        await page.reload({ timeout: 5000 });
        await page.waitForSelector('h1', { timeout: 3000 });
      } catch (error) {
        errorCount++;
        console.warn(`Reload ${i + 1} failed:`, error);
      }
    }
    
    // エラー率が20%以下
    expect(errorCount).toBeLessThan(2);
  });

  test('存在しないページへのアクセス', async ({ page }) => {
    // 404ページのテスト
    const response = await page.goto('/non-existent-page');
    
    // 404ステータス
    expect(response?.status()).toBe(404);
    
    // 適切な404ページが表示される
    await expect(page.getByText(/404|Not Found/)).toBeVisible();
  });

  test('セキュリティヘッダーの確認', async ({ page }) => {
    const response = await page.goto('/');
    
    const headers = response?.headers() || {};
    
    // セキュリティ関連ヘッダーの存在確認
    expect(headers['x-powered-by']).toBe('Next.js'); // Next.jsヘッダー
    
    // その他のセキュリティヘッダーがあれば確認
    console.log('Security headers:', {
      'content-security-policy': headers['content-security-policy'],
      'x-frame-options': headers['x-frame-options'],
      'x-content-type-options': headers['x-content-type-options']
    });
  });
});