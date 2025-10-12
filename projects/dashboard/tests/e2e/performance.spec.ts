import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('ページ読み込み速度', async ({ page }) => {
    const startTime = Date.now();
    
    // より現実的な条件でページ読み込み
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('h1', { timeout: 5000 });
    
    const loadTime = Date.now() - startTime;
    console.log(`Page load time: ${loadTime}ms`);
    
    // 8秒以内で読み込み完了（現実的な時間）
    expect(loadTime).toBeLessThan(8000);
  });

  test('メモリ使用量チェック', async ({ page }) => {
    await page.goto('/');

    // ページ読み込み後、メモリリークがないか
    const initialMetrics = await page.evaluate(() => {
      const memory = (performance as { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory;
      return memory ? {
        usedJSHeapSize: memory.usedJSHeapSize || 0,
        totalJSHeapSize: memory.totalJSHeapSize || 0
      } : null;
    });
    
    // 何度かページ更新してメモリ使用量をチェック
    for (let i = 0; i < 3; i++) {
      await page.reload();
      await page.waitForTimeout(1000);
    }
    
    const finalMetrics = await page.evaluate(() => {
      const memory = (performance as { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory;
      return memory ? {
        usedJSHeapSize: memory.usedJSHeapSize || 0,
        totalJSHeapSize: memory.totalJSHeapSize || 0
      } : null;
    });
    
    if (initialMetrics && finalMetrics && 
        typeof initialMetrics.usedJSHeapSize === 'number' && 
        typeof finalMetrics.usedJSHeapSize === 'number') {
      // メモリ使用量が大幅に増加していないか（100MB以内）
      const memoryIncrease = finalMetrics.usedJSHeapSize - initialMetrics.usedJSHeapSize;
      console.log(`Memory increase: ${memoryIncrease} bytes`);
      expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024); // 100MB
    } else {
      // メモリAPIが利用できない場合はスキップ
      console.log('Memory API not available, skipping memory test');
      expect(true).toBe(true); // テストをパスさせる
    }
  });

  test('大量データ表示性能', async ({ page }) => {
    await page.goto('/');
    
    // サービスカードの描画性能
    const startTime = Date.now();
    
    // すべてのサービスカードが表示されるまで待機
    await page.waitForSelector('.grid > div', { timeout: 5000 });
    
    const renderTime = Date.now() - startTime;
    console.log(`Service cards render time: ${renderTime}ms`);
    
    // 2秒以内で描画完了
    expect(renderTime).toBeLessThan(2000);
  });

  test('レスポンシブ切り替え性能', async ({ page }) => {
    await page.goto('/');
    
    // デスクトップ→モバイル→デスクトップの切り替え時間
    const startTime = Date.now();
    
    await page.setViewportSize({ width: 375, height: 667 }); // Mobile
    await page.waitForTimeout(100);
    
    await page.setViewportSize({ width: 1920, height: 1080 }); // Desktop
    await page.waitForTimeout(100);
    
    const switchTime = Date.now() - startTime;
    console.log(`Responsive switch time: ${switchTime}ms`);
    
    // 1秒以内でレスポンシブ切り替え
    expect(switchTime).toBeLessThan(1000);
  });
});