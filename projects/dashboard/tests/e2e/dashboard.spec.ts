import { test, expect } from '@playwright/test';

test.describe('統合ダッシュボード E2E', () => {
  test('ダッシュボードの基本機能が動作する', async ({ page }) => {
    // ダッシュボードにアクセス
    await page.goto('/');

    // ページタイトルが正しい
    await expect(page).toHaveTitle(/統合ダッシュボード/);

    // メインヘッダーが表示される（実際のテキストに合わせる）
    await expect(page.getByRole('heading', { name: /統合ダッシュボード/ })).toBeVisible();

    // サービス名が表示される（最初の要素のみチェック）
    await expect(page.getByText('Code Server').first()).toBeVisible();
    await expect(page.getByText('Syncthing')).toBeVisible(); 
    await expect(page.getByText('NATS')).toBeVisible();
    await expect(page.getByText('MediaMTX')).toBeVisible();
    await expect(page.getByText('OpenAI Realtime')).toBeVisible();
  });

  test('サービスの状態チェック機能', async ({ page }) => {
    await page.goto('/');

    // 少し待ってサービス状態が更新されるのを待つ
    await page.waitForTimeout(3000);

    // サービス状態表示の確認（Online/Offline状態）
    const statusElements = page.getByText(/Online|Offline|Checking/);
    const count = await statusElements.count();
    expect(count).toBeGreaterThanOrEqual(1);

    // 直接アクセスリンクが存在する
    const accessLinks = page.getByText('直接アクセス');
    const linkCount = await accessLinks.count();
    expect(linkCount).toBeGreaterThanOrEqual(3);
  });

  test('統合アクセスセクションの表示', async ({ page }) => {
    await page.goto('/');

    // 統合アクセスセクションのヘッダー確認
    await expect(page.getByRole('heading', { name: /統合アクセス/ })).toBeVisible();

    // 統合アクセスのリンク確認
    const codeServerLinks = page.getByText('Code Server');
    const codeServerCount = await codeServerLinks.count();
    expect(codeServerCount).toBeGreaterThanOrEqual(1);
    
    await expect(page.getByText('Voice Chat').first()).toBeVisible();
  });

  test('レスポンシブデザイン - モバイル', async ({ page }) => {
    // モバイルサイズに設定
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // メインヘッダーがモバイルでも表示される
    await expect(page.getByRole('heading', { name: /統合ダッシュボード/ })).toBeVisible();

    // サービス名がモバイルでも表示される
    const mobileCodeServerLinks = page.getByText('Code Server');
    const mobileCount = await mobileCodeServerLinks.count();
    expect(mobileCount).toBeGreaterThanOrEqual(1);
  });
});