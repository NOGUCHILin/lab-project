/**
 * 🚀 REFACTORED SERVICES CONFIGURATION
 * Now using environment variables for flexibility
 * No more hardcoded URLs - configuration via .env files
 */

import { env } from '@/lib/env';
import { buildDynamicServiceUrl } from '@/lib/config/dynamic-url';

export interface Service {
  id: string;
  name: string;
  url: string;
  icon: string;
  description: string;
  category: 'ai' | 'development' | 'storage' | 'infrastructure';
  healthCheck?: string;
  status?: 'active' | 'deprecated' | 'maintenance';
  tags?: string[];
  features?: string[];  // 主な機能リスト
  docsUrl?: string;     // 使い方・ドキュメントへのリンク
}

// Use dynamic URL builder instead of env.BASE_URL
const buildServiceUrl = buildDynamicServiceUrl;

export const SERVICES: Service[] = [
  // Development Tools
  {
    id: 'applebuyers-article-editor',
    name: '記事編集 (Code Server)',
    url: 'https://home-lab-01.tail4ed625.ts.net:8890/',
    icon: '📝',
    description: 'AppleBuyers記事をMarkdownで編集 (~/projects/applebuyers_application/public-site/content/articles/)',
    category: 'development',
    tags: ['editor', 'writing', 'markdown', 'applebuyers'],
    features: ['Markdown記事編集', '画像アップロード', 'リアルタイムプレビュー'],
    status: 'active'
  },
  {
    id: 'code-server',
    name: 'Code Server',
    url: 'https://home-lab-01.tail4ed625.ts.net:8889/',
    icon: '💻',
    description: 'Browser-based VSCode',
    category: 'development',
    healthCheck: 'https://home-lab-01.tail4ed625.ts.net:8889/healthz',
    tags: ['editor', 'development'],
    features: ['ブラウザでVSCodeを使用', 'リモート開発環境', '拡張機能サポート'],
    docsUrl: 'https://github.com/coder/code-server/blob/main/docs/guide.md'
  },
  {
    id: 'applebuyers-preview',
    name: '記事プレビュー',
    url: 'https://home-lab-01.tail4ed625.ts.net:13005/',
    icon: '👁️',
    description: 'AppleBuyers Public Siteのプレビュー表示',
    category: 'development',
    tags: ['preview', 'applebuyers', 'nextjs'],
    features: ['編集中記事のプレビュー', 'Next.js開発サーバー'],
    status: 'active'
  },

  // AI Services

  // Storage & File Management
  {
    id: 'syncthing',
    name: 'Syncthing',
    url: buildServiceUrl(env.SYNCTHING_PORT, '/'),
    icon: '🔄',
    description: 'File synchronization',
    category: 'storage',
    healthCheck: buildServiceUrl(env.SYNCTHING_PORT, '/rest/noauth/health'),
    tags: ['sync', 'files'],
    features: ['P2Pファイル同期', '暗号化通信', 'マルチデバイス対応'],
    docsUrl: 'https://docs.syncthing.net/'
  },
  {
    id: 'file-manager',
    name: 'File Manager',
    url: buildServiceUrl(env.FILE_MANAGER_PORT, '/'),
    icon: '📁',
    description: 'Web-based file management',
    category: 'storage',
    healthCheck: buildServiceUrl(env.FILE_MANAGER_PORT, '/api/public/dl/nopass'),
    tags: ['files', 'manager'],
    features: ['Webファイルブラウザ', 'アップロード/ダウンロード', 'ファイル編集'],
    docsUrl: 'https://github.com/filebrowser/filebrowser'
  },

  // Infrastructure
  {
    id: 'nats',
    name: 'NATS',
    url: buildServiceUrl(env.NATS_PORT, '/'),
    icon: '📡',
    description: 'Event-driven messaging',
    category: 'infrastructure',
    healthCheck: buildServiceUrl(env.NATS_PORT, '/varz'),
    tags: ['messaging', 'events'],
    features: ['高速メッセージング', 'Pub/Sub', 'マイクロサービス通信'],
    docsUrl: 'https://docs.nats.io/'
  },

  // Dashboard itself (for completeness)
  {
    id: 'dashboard',
    name: 'Dashboard',
    url: '/',
    icon: '🏠',
    description: 'Service monitoring and management',
    category: 'infrastructure',
    status: 'active',
    tags: ['dashboard', 'home']
  },

  // Nakamura-Misaki (Claude Agent)
  {
    id: 'nakamura-misaki',
    name: 'Nakamura-Misaki',
    url: buildServiceUrl(3002, '/'),
    icon: '🤖',
    description: 'Multi-user Claude Code Agent - Admin UI',
    category: 'ai',
    healthCheck: buildServiceUrl(8010, '/health'),
    tags: ['ai', 'claude', 'agent', 'slack', 'admin'],
    features: ['Slack統合', 'マルチユーザー対応', 'プロンプト管理', 'タスク管理', 'エラーログ監視'],
    docsUrl: '/projects/nakamura-misaki/README.md',
    status: 'active'
  }
];

// Utility functions
export const getServicesByCategory = (category: Service['category']): Service[] =>
  SERVICES.filter(service => service.category === category);

export const getActiveServices = (): Service[] =>
  SERVICES.filter(service => service.status !== 'deprecated');

export const getServiceById = (id: string): Service | undefined =>
  SERVICES.find(service => service.id === id);

export const getServicesByTag = (tag: string): Service[] =>
  SERVICES.filter(service => service.tags?.includes(tag));

// Export for easy import
export default SERVICES;
