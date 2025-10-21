/**
 * 🚀 NEW SIMPLIFIED Dashboard Page
 * Server-side service loading from NixOS registry
 */

import { ServiceGrid } from '@/components/services/ServiceGrid';
import { transformNixOSRegistry, getServicesByCategory, type Service } from '@/config/services';
import fs from 'fs';

// Force dynamic rendering to read services.json at runtime (not build time)
export const dynamic = 'force-dynamic';

async function getServices(): Promise<Service[]> {
  const servicesPath = process.env.SERVICES_CONFIG || '/etc/unified-dashboard/services.json';

  try {
    // Direct file read (server-side only)
    const rawData = fs.readFileSync(servicesPath, 'utf-8');
    const registry = JSON.parse(rawData);
    return transformNixOSRegistry(registry);
  } catch (error) {
    console.error('Error loading services:', error);
    return [];
  }
}

export default async function UnifiedDashboard() {
  const services = await getServices();

  // Simple stats calculation
  const stats = {
    total: services.length,
    ai: getServicesByCategory(services, 'ai').length,
    development: getServicesByCategory(services, 'development').length,
    storage: getServicesByCategory(services, 'storage').length,
    infrastructure: getServicesByCategory(services, 'infrastructure').length
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            🚀 統合ダッシュボード
          </h1>
          <p className="text-xl text-gray-300">
            NixOS上の全サービスを一元管理 - 次世代サービスレジストリ
          </p>

          {/* Quick Stats */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700">
              <div className="text-2xl font-bold text-white">{stats.total}</div>
              <div className="text-sm text-gray-400">総サービス</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700">
              <div className="text-2xl font-bold text-blue-400">{stats.ai}</div>
              <div className="text-sm text-gray-400">AI</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700">
              <div className="text-2xl font-bold text-green-400">{stats.development}</div>
              <div className="text-sm text-gray-400">開発</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700">
              <div className="text-2xl font-bold text-purple-400">{stats.storage}</div>
              <div className="text-sm text-gray-400">ストレージ</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700">
              <div className="text-2xl font-bold text-orange-400">{stats.infrastructure}</div>
              <div className="text-sm text-gray-400">インフラ</div>
            </div>
          </div>
        </header>

        {/* Services Grid */}
        <ServiceGrid services={services} columns={3} />

        {/* System Information */}
        <section className="bg-gray-800 rounded-lg p-8 mt-12 border border-gray-700">
          <h2 className="text-3xl font-bold text-white mb-6">ℹ️ システム情報</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-900 p-6 rounded-lg border border-gray-600">
              <h3 className="text-lg font-semibold text-blue-400 mb-2">OS</h3>
              <p className="text-gray-300">NixOS 25.05</p>
              <p className="text-sm text-gray-500 mt-1">宣言的システム管理</p>
            </div>
            <div className="bg-gray-900 p-6 rounded-lg border border-gray-600">
              <h3 className="text-lg font-semibold text-green-400 mb-2">Network</h3>
              <p className="text-gray-300">Tailscale VPN</p>
              <p className="text-sm text-gray-500 mt-1">セキュアなリモートアクセス</p>
            </div>
            <div className="bg-gray-900 p-6 rounded-lg border border-gray-600">
              <h3 className="text-lg font-semibold text-purple-400 mb-2">Architecture</h3>
              <p className="text-gray-300">シンプルリンク集</p>
              <p className="text-sm text-gray-500 mt-1">直接接続・高速アクセス</p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm border-t border-gray-700 pt-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <h4 className="font-semibold text-gray-400 mb-2">技術スタック</h4>
              <p>Next.js 15 + TypeScript + Tailwind CSS</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-400 mb-2">アーキテクチャ</h4>
              <p>シンプル・高速・保守性重視</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-400 mb-2">バージョン</h4>
              <p>v2.0.0 - 完全簡素化版</p>
            </div>
          </div>
          <p className="text-xs">
            🚀 Simple Dashboard v2.0 - No Complex APIs, Just Pure Links
          </p>
        </footer>
      </div>
    </main>
  );
}