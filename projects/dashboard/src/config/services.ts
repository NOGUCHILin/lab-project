/**
 * 🚀 NixOS統合サービス設定
 * NixOSレジストリ（/etc/unified-dashboard/services.json）から動的に読み込み
 * 単一の真実の情報源（Single Source of Truth）を実現
 */

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
  features?: string[];
  docsUrl?: string;
  port?: number;
  path?: string;
  apiUrl?: string;
}

interface NixOSServiceRegistry {
  [key: string]: {
    name: string;
    description: string;
    icon: string;
    port: number;
    path: string;
    url: string;
    apiUrl: string;
    healthCheck: string;
  };
}

// カテゴリマッピング（サービス名からカテゴリを推定）
const inferCategory = (serviceName: string): Service['category'] => {
  const name = serviceName.toLowerCase();
  if (name.includes('nakamura') || name.includes('ai')) return 'ai';
  if (name.includes('code') || name.includes('editor') || name.includes('preview') || name.includes('applebuyers')) return 'development';
  if (name.includes('file') || name.includes('syncthing')) return 'storage';
  return 'infrastructure';
};

// タグ生成（サービス特性からタグを推定）
const inferTags = (serviceName: string, description: string): string[] => {
  const tags: string[] = [];
  const text = `${serviceName} ${description}`.toLowerCase();

  if (text.includes('editor') || text.includes('vscode')) tags.push('editor');
  if (text.includes('applebuyers')) tags.push('applebuyers');
  if (text.includes('slack')) tags.push('slack');
  if (text.includes('claude')) tags.push('claude', 'ai');
  if (text.includes('file')) tags.push('files');
  if (text.includes('sync')) tags.push('sync');
  if (text.includes('preview')) tags.push('preview');
  if (text.includes('dashboard')) tags.push('dashboard', 'home');

  return tags;
};

// 機能リスト生成（サービスタイプから推定）
const inferFeatures = (serviceName: string, id: string): string[] => {
  const featuresMap: Record<string, string[]> = {
    'nakamuraMisaki': ['Slack統合', 'マルチユーザー対応', 'プロンプト管理', 'タスク管理', 'エラーログ監視'],
    'codeServer': ['ブラウザでVSCodeを使用', 'リモート開発環境', '拡張機能サポート'],
    'applebuyersWriterEditor': ['Markdown記事編集', '画像アップロード', 'リアルタイムプレビュー'],
    'applebuyersPreview': ['編集中記事のプレビュー', 'Next.js開発サーバー'],
    'fileManager': ['Webファイルブラウザ', 'アップロード/ダウンロード', 'ファイル編集'],
    'syncthing': ['P2Pファイル同期', '暗号化通信', 'マルチデバイス対応'],
    'nats': ['高速メッセージング', 'Pub/Sub', 'マイクロサービス通信'],
    'n8n': ['ワークフロー自動化', 'ノーコード統合', 'API連携'],
  };

  return featuresMap[id] || [];
};

// ドキュメントURL生成
const inferDocsUrl = (id: string): string | undefined => {
  const docsMap: Record<string, string> = {
    'nakamuraMisaki': '/projects/nakamura-misaki/README.md',
    'codeServer': 'https://github.com/coder/code-server/blob/main/docs/guide.md',
    'fileManager': 'https://github.com/filebrowser/filebrowser',
    'syncthing': 'https://docs.syncthing.net/',
    'nats': 'https://docs.nats.io/',
    'n8n': 'https://docs.n8n.io/',
  };

  return docsMap[id];
};

/**
 * NixOSレジストリからサービスを生成
 * APIルート経由で取得したレジストリデータからServiceオブジェクトを生成
 */
export function transformNixOSRegistry(registry: NixOSServiceRegistry): Service[] {
  return Object.entries(registry).map(([id, service]) => ({
    id,
    name: service.name,
    url: service.url,
    icon: service.icon,
    description: service.description,
    category: inferCategory(service.name),
    healthCheck: service.url + service.healthCheck,
    status: 'active' as const,
    tags: inferTags(service.name, service.description),
    features: inferFeatures(service.name, id),
    docsUrl: inferDocsUrl(id),
    port: service.port,
    path: service.path,
    apiUrl: service.apiUrl,
  }));
}

// Utility functions (now accept services array as parameter)
export const getServicesByCategory = (services: Service[], category: Service['category']): Service[] =>
  services.filter(service => service.category === category);

export const getActiveServices = (services: Service[]): Service[] =>
  services.filter(service => service.status !== 'deprecated');

export const getServiceById = (services: Service[], id: string): Service | undefined =>
  services.find(service => service.id === id);

export const getServicesByTag = (services: Service[], tag: string): Service[] =>
  services.filter(service => service.tags?.includes(tag));
