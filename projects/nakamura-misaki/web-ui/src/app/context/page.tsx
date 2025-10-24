'use client';

import { useState } from 'react';

interface ContextSettings {
  contextWindow: number;
  compressionThreshold: number;
  recentMessagesToKeep: number;
  conversationTtlHours: number;
  model: string;
  maxTokens: number;
}

// Current hardcoded settings from backend (context_manager.py, config.py, claude_agent_service.py)
const CURRENT_SETTINGS: ContextSettings = {
  contextWindow: 200000,
  compressionThreshold: 0.8,
  recentMessagesToKeep: 10,
  conversationTtlHours: 24,
  model: 'claude-3-5-sonnet-20241022',
  maxTokens: 4096,
};

export default function ContextManagementPage() {
  const [settings] = useState<ContextSettings>(CURRENT_SETTINGS);

  const compressionThresholdTokens = Math.floor(settings.contextWindow * settings.compressionThreshold);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          🧠 コンテキスト管理
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Anthropic推奨のコンテキストエンジニアリング設定を管理します
        </p>
      </div>

      {/* Alert: Future Enhancement Notice */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">現在は読み取り専用</h3>
            <p className="mt-1 text-sm text-blue-700">
              設定の編集機能は今後実装予定です。現在はバックエンドのPythonコードで定義された値を表示しています。
            </p>
          </div>
        </div>
      </div>

      {/* Context Compression Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-5 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">✂️ コンテキスト圧縮設定</h2>
          <p className="mt-1 text-sm text-gray-600">
            Anthropic推奨の「Compaction」戦略 - トークン使用量を最大84%削減
          </p>
        </div>
        <div className="px-6 py-5 space-y-6">
          {/* Context Window */}
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                コンテキストウィンドウ
              </label>
              <p className="mt-1 text-sm text-gray-500">
                Claude 3.5 Sonnetの最大コンテキスト長
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                {settings.contextWindow.toLocaleString()} トークン
              </span>
            </div>
          </div>

          {/* Compression Threshold */}
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                圧縮閾値
              </label>
              <p className="mt-1 text-sm text-gray-500">
                この割合に達すると自動圧縮を実行 ({compressionThresholdTokens.toLocaleString()} トークン到達時)
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                {(settings.compressionThreshold * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Recent Messages to Keep */}
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                最近メッセージ保持数
              </label>
              <p className="mt-1 text-sm text-gray-500">
                圧縮時に保持する最新メッセージの数（古いメッセージは要約される）
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                {settings.recentMessagesToKeep} 件
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Conversation Management Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-5 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">💬 会話管理設定</h2>
          <p className="mt-1 text-sm text-gray-600">
            会話セッションのライフサイクル設定
          </p>
        </div>
        <div className="px-6 py-5 space-y-6">
          {/* Conversation TTL */}
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                会話有効期限 (TTL)
              </label>
              <p className="mt-1 text-sm text-gray-500">
                会話セッションが自動削除されるまでの時間
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {settings.conversationTtlHours} 時間
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Claude API Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-6 py-5 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">🤖 Claude API設定</h2>
          <p className="mt-1 text-sm text-gray-600">
            Claude API呼び出しのパラメータ
          </p>
        </div>
        <div className="px-6 py-5 space-y-6">
          {/* Model */}
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                使用モデル
              </label>
              <p className="mt-1 text-sm text-gray-500">
                Claude API呼び出しで使用するモデル
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                {settings.model}
              </span>
            </div>
          </div>

          {/* Max Tokens */}
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">
                最大出力トークン数
              </label>
              <p className="mt-1 text-sm text-gray-500">
                Claude応答の最大トークン数
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-pink-100 text-pink-800">
                {settings.maxTokens.toLocaleString()} トークン
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Implementation Details */}
      <div className="bg-gray-50 shadow rounded-lg">
        <div className="px-6 py-5 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">📚 実装詳細</h2>
        </div>
        <div className="px-6 py-5">
          <div className="space-y-4 text-sm text-gray-700">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">コンテキスト圧縮の仕組み</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li>トークン数が閾値（80%）に達すると自動的に圧縮を実行</li>
                <li>古いメッセージをClaude自身が要約</li>
                <li>最新10件のメッセージは要約せずそのまま保持</li>
                <li>要約結果をconversation_summaryタグでラップして挿入</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">トークン推定方法</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li>日本語: 1文字 ≈ 0.4トークン</li>
                <li>英語: 1文字 ≈ 0.25トークン</li>
                <li>平均: 1文字 ≈ 0.35トークン（日英混在を考慮）</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">実装ファイル</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600 font-mono text-xs">
                <li>projects/nakamura-misaki/src/infrastructure/context_manager.py</li>
                <li>projects/nakamura-misaki/src/infrastructure/config.py</li>
                <li>projects/nakamura-misaki/src/contexts/conversations/domain/services/claude_agent_service.py</li>
              </ul>
            </div>
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
              <h3 className="font-medium text-blue-900 mb-2">今後の拡張案</h3>
              <ul className="list-disc list-inside space-y-1 text-blue-700 text-sm">
                <li>設定変更API実装（POST /api/context/settings）</li>
                <li>トークン使用量の可視化グラフ</li>
                <li>圧縮履歴の表示</li>
                <li>Prompt Caching設定（コスト90%削減）</li>
                <li>モデル選択（Sonnet/Haiku切り替え）</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
