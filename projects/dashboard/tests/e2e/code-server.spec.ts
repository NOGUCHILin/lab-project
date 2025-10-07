import { test, expect } from '@playwright/test';

test.describe('Code Server Integration', () => {
  test.beforeEach(async ({ page }) => {
    // ダッシュボードに移動
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Code Server card should be visible and clickable', async ({ page }) => {
    // Code Serverカードを探す
    const codeServerCard = page.locator('[data-testid="service-card-code-server"], div:has-text("Code Server")').first();
    
    // カードが表示されているか確認
    await expect(codeServerCard).toBeVisible({ timeout: 10000 });
    
    // カードの要素を確認
    const cardText = await codeServerCard.textContent();
    expect(cardText).toContain('Code Server');
    expect(cardText).toContain('ブラウザベースのVSCode');
    
    // アイコンが表示されているか
    const icon = codeServerCard.locator('text=💻');
    await expect(icon).toBeVisible();
  });

  test('Code Server link should open in new tab', async ({ page, context }) => {
    // Code Serverカードのリンクを取得
    const codeServerLink = page.locator('a:has-text("Code Server")').first();
    
    // リンクが存在することを確認
    await expect(codeServerLink).toBeVisible({ timeout: 10000 });
    
    // href属性を確認
    const href = await codeServerLink.getAttribute('href');
    expect(href).toBe('https://nixos.tail4ed625.ts.net/code/');
    
    // target="_blank"属性を確認
    const target = await codeServerLink.getAttribute('target');
    expect(target).toBe('_blank');
    
    // 新しいタブが開くことをテスト
    const [newPage] = await Promise.all([
      context.waitForEvent('page'),
      codeServerLink.click()
    ]);
    
    // 新しいページのURLを確認
    await newPage.waitForLoadState('domcontentloaded');
    const newPageUrl = newPage.url();
    expect(newPageUrl).toContain('nixos.tail4ed625.ts.net');
    
    // Code Serverページが正常にロードされたか確認
    // Code Serverのページタイトルまたは特定の要素を確認
    await newPage.waitForTimeout(3000); // ページの読み込みを待つ
    
    // ページのタイトルを確認（Code Serverの場合）
    const title = await newPage.title();
    console.log('Code Server page title:', title);
    
    // ページのコンテンツが存在するか確認
    const bodyContent = await newPage.locator('body').textContent();
    expect(bodyContent).toBeTruthy();
    
    await newPage.close();
  });

  test('Code Server health check should work', async ({ page }) => {
    // ヘルスチェックAPIを直接テスト
    const response = await page.request.get('/api/health/8889');
    
    // レスポンスステータスを確認
    expect(response.status()).toBe(200);
    
    // レスポンス内容を確認
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(['healthy', 'unhealthy']).toContain(data.status);
    
    if (data.status === 'healthy') {
      expect(data).toHaveProperty('service', 'code-server');
      expect(data).toHaveProperty('timestamp');
    }
  });

  test('Code Server service status indicator', async ({ page }) => {
    // Code Serverカードを探す
    const codeServerCard = page.locator('[data-testid="service-card-code-server"], div:has-text("Code Server")').first();
    
    // ステータスインジケーターを探す（通常は緑色の点やアイコン）
    const statusIndicator = codeServerCard.locator('[data-testid="service-status"], .status-indicator, svg, .text-green-500, .text-red-500').first();
    
    // ステータスインジケーターが存在するか確認
    // Note: 実際のUIに応じて調整が必要
    if (await statusIndicator.count() > 0) {
      await expect(statusIndicator).toBeVisible();
      
      // クラス名からステータスを判断
      const className = await statusIndicator.getAttribute('class');
      console.log('Status indicator class:', className);
      
      // 緑色（健全）または赤色（不健全）のいずれかであることを確認
      if (className) {
        const isHealthy = className.includes('green') || className.includes('success');
        const isUnhealthy = className.includes('red') || className.includes('error');
        expect(isHealthy || isUnhealthy).toBeTruthy();
      }
    }
  });
});