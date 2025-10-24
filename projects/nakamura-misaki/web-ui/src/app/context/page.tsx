'use client';

import { useEffect, useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { promptApi, Prompt } from '@/lib/api';
import {
  analyzePrompt,
  getCachingRecommendations,
  getTokenBgColor,
  getTokenColor,
  countTokens,
} from '@/lib/prompt-utils';

interface ContextSettings {
  contextWindow: number;
  compressionThreshold: number;
  recentMessagesToKeep: number;
  conversationTtlHours: number;
  model: string;
  maxTokens: number;
}

const CURRENT_SETTINGS: ContextSettings = {
  contextWindow: 200000,
  compressionThreshold: 0.8,
  recentMessagesToKeep: 10,
  conversationTtlHours: 24,
  model: 'claude-3-5-sonnet-20241022',
  maxTokens: 4096,
};

type TabType = 'prompts' | 'settings';

export default function ContextManagementPage() {
  const [activeTab, setActiveTab] = useState<TabType>('prompts');
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings] = useState<ContextSettings>(CURRENT_SETTINGS);

  const ACTIVE_PROMPT_NAME = 'default';

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      const data = await promptApi.list();
      setPrompts(data);
      if (data.length > 0 && !selectedPrompt) {
        setSelectedPrompt(data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedPrompt) return;

    setSaving(true);
    try {
      await promptApi.update(selectedPrompt);
      await fetchPrompts();
      setEditing(false);
      alert('プロンプトを保存しました');
    } catch (error) {
      console.error('Failed to save prompt:', error);
      alert('保存に失敗しました');
    } finally {
      setSaving(false);
    }
  };

  const analysis = useMemo(
    () => (selectedPrompt ? analyzePrompt(selectedPrompt.system_prompt) : null),
    [selectedPrompt?.system_prompt]
  );

  const cachingInfo = useMemo(
    () => (analysis ? getCachingRecommendations(analysis.tokenCount) : null),
    [analysis?.tokenCount]
  );

  const compressionThresholdTokens = Math.floor(
    settings.contextWindow * settings.compressionThreshold
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold flex items-center gap-2">
            🧠 コンテキスト管理
          </h1>
          <p className="text-sm text-gray-600 mt-2">
            Anthropic Context Engineering Principles 準拠
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('prompts')}
                className={`${
                  activeTab === 'prompts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                ✏️ プロンプト編集
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`${
                  activeTab === 'settings'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                ⚙️ コンテキスト設定
              </button>
            </nav>
          </div>
        </div>

        {/* Prompts Tab */}
        {activeTab === 'prompts' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
            {/* プロンプト一覧 */}
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>プロンプト一覧</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {prompts.map((prompt) => {
                    const tokenCount = countTokens(prompt.system_prompt);
                    const isActive = prompt.name === ACTIVE_PROMPT_NAME;

                    return (
                      <button
                        key={prompt.name}
                        onClick={() => {
                          setSelectedPrompt(prompt);
                          setEditing(false);
                        }}
                        className={`w-full text-left px-4 py-3 rounded-lg transition-colors border ${
                          selectedPrompt?.name === prompt.name
                            ? 'bg-blue-100 text-blue-900 border-blue-300'
                            : 'hover:bg-gray-100 border-transparent'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <div className="font-medium">{prompt.name}</div>
                          {isActive && (
                            <span className="text-xs bg-green-500 text-white px-2 py-1 rounded">
                              ✓ 適用中
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 mb-2">
                          {prompt.version}
                        </div>
                        <div
                          className={`text-xs px-2 py-1 rounded inline-block ${getTokenBgColor(
                            tokenCount
                          )}`}
                        >
                          {tokenCount.toLocaleString()} tokens
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* プロンプト編集エリア */}
            <Card className="lg:col-span-6">
              <CardHeader>
                <div className="flex justify-between items-center flex-wrap gap-2">
                  <div>
                    <CardTitle className="mb-1">
                      {selectedPrompt?.name || 'プロンプト未選択'}
                    </CardTitle>
                    {analysis && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={`text-sm font-semibold ${getTokenColor(
                            analysis.tokenCount
                          )}`}
                        >
                          {analysis.tokenCount.toLocaleString()} tokens
                        </span>
                        <span className="text-xs text-gray-500">
                          構造スコア: {analysis.structureScore}/100
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="space-x-2">
                    {editing ? (
                      <>
                        <Button
                          variant="outline"
                          onClick={() => {
                            setEditing(false);
                            fetchPrompts();
                          }}
                        >
                          キャンセル
                        </Button>
                        <Button onClick={handleSave} disabled={saving}>
                          {saving ? '保存中...' : '保存'}
                        </Button>
                      </>
                    ) : (
                      <Button onClick={() => setEditing(true)}>編集</Button>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {selectedPrompt ? (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="description">説明</Label>
                      <Input
                        id="description"
                        value={selectedPrompt.description}
                        onChange={(e) =>
                          setSelectedPrompt({
                            ...selectedPrompt,
                            description: e.target.value,
                          })
                        }
                        disabled={!editing}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="version">バージョン</Label>
                      <Input
                        id="version"
                        value={selectedPrompt.version}
                        onChange={(e) =>
                          setSelectedPrompt({
                            ...selectedPrompt,
                            version: e.target.value,
                          })
                        }
                        disabled={!editing}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="system_prompt">システムプロンプト</Label>
                      <Textarea
                        id="system_prompt"
                        value={selectedPrompt.system_prompt}
                        onChange={(e) =>
                          setSelectedPrompt({
                            ...selectedPrompt,
                            system_prompt: e.target.value,
                          })
                        }
                        disabled={!editing}
                        className="mt-1 font-mono text-sm"
                        rows={25}
                      />
                    </div>

                    {/* 構造分析パネル */}
                    {analysis && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h3 className="font-semibold text-blue-900 mb-3">
                          構造分析
                        </h3>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex items-center">
                            {analysis.hasXmlStructure ? '✅' : '❌'} XML構造
                          </div>
                          <div className="flex items-center">
                            {analysis.hasExamples ? '✅' : '❌'} 具体例
                          </div>
                          <div className="flex items-center">
                            {analysis.hasInstructions ? '✅' : '❌'} 明確なルール
                          </div>
                          <div className="flex items-center">
                            {analysis.isConcise ? '✅' : '❌'} 簡潔性 (&lt;5K)
                          </div>
                        </div>

                        {analysis.xmlTags.length > 0 && (
                          <div className="mt-3">
                            <div className="text-xs text-gray-700 mb-1">
                              検出されたXMLタグ:
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {analysis.xmlTags.map((tag) => (
                                <span
                                  key={tag}
                                  className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                                >
                                  &lt;{tag}&gt;
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {cachingInfo && cachingInfo.shouldCache && (
                          <div className="mt-3 bg-green-100 text-green-900 p-2 rounded text-sm">
                            💰 キャッシング推奨: {cachingInfo.estimatedSavings}
                          </div>
                        )}

                        {analysis.recommendations.length > 0 && (
                          <div className="mt-3">
                            <div className="text-xs font-semibold text-gray-700 mb-1">
                              改善推奨事項:
                            </div>
                            <ul className="text-xs text-gray-700 space-y-1 list-disc list-inside">
                              {analysis.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="text-sm text-gray-500">
                      <div>
                        作成日時:{' '}
                        {new Date(selectedPrompt.created_at).toLocaleString(
                          'ja-JP'
                        )}
                      </div>
                      <div>
                        更新日時:{' '}
                        {new Date(selectedPrompt.updated_at).toLocaleString(
                          'ja-JP'
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">左からプロンプトを選択してください</p>
                )}
              </CardContent>
            </Card>

            {/* Anthropic Best Practices パネル */}
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle className="text-base">
                  Anthropic Best Practices
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Context Engineering</h4>
                  <ul className="space-y-1 text-xs text-gray-700">
                    <li className="flex items-start">
                      <span className="mr-2">📐</span>
                      <span>
                        <strong>構造化:</strong> XMLタグで明確に区分
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">📚</span>
                      <span>
                        <strong>具体例:</strong> &lt;example&gt;で提示
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">✂️</span>
                      <span>
                        <strong>簡潔性:</strong> 5000トークン以下推奨
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mr-2">💾</span>
                      <span>
                        <strong>キャッシング:</strong> 1024+トークンで有効
                      </span>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">推奨XMLタグ</h4>
                  <div className="flex flex-wrap gap-1">
                    {[
                      'instructions',
                      'example',
                      'context',
                      'thinking',
                      'document',
                    ].map((tag) => (
                      <code
                        key={tag}
                        className="text-xs bg-gray-100 px-2 py-1 rounded"
                      >
                        &lt;{tag}&gt;
                      </code>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">トークン閾値</h4>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center">
                      <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                      <span>&lt;2K: 最適</span>
                    </div>
                    <div className="flex items-center">
                      <span className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                      <span>2-5K: 良好</span>
                    </div>
                    <div className="flex items-center">
                      <span className="w-3 h-3 bg-orange-500 rounded-full mr-2"></span>
                      <span>5-10K: 要改善</span>
                    </div>
                    <div className="flex items-center">
                      <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                      <span>&gt;10K: 圧縮推奨</span>
                    </div>
                  </div>
                </div>

                <a
                  href="https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-xs text-blue-600 hover:underline"
                >
                  📖 Prompt Engineering Guide →
                </a>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            {/* Alert: Future Enhancement Notice */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-blue-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    現在は読み取り専用
                  </h3>
                  <p className="mt-1 text-sm text-blue-700">
                    設定の編集機能は今後実装予定です。現在はバックエンドのPythonコードで定義された値を表示しています。
                  </p>
                </div>
              </div>
            </div>

            {/* Context Compression Settings */}
            <Card>
              <CardHeader>
                <CardTitle>✂️ コンテキスト圧縮設定</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Anthropic推奨の「Compaction」戦略 - トークン使用量を最大84%削減
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
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

                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">
                      圧縮閾値
                    </label>
                    <p className="mt-1 text-sm text-gray-500">
                      この割合に達すると自動圧縮を実行 (
                      {compressionThresholdTokens.toLocaleString()}{' '}
                      トークン到達時)
                    </p>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                      {(settings.compressionThreshold * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

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
              </CardContent>
            </Card>

            {/* Conversation Management Settings */}
            <Card>
              <CardHeader>
                <CardTitle>💬 会話管理設定</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  会話セッションのライフサイクル設定
                </p>
              </CardHeader>
              <CardContent>
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
              </CardContent>
            </Card>

            {/* Claude API Settings */}
            <Card>
              <CardHeader>
                <CardTitle>🤖 Claude API設定</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Claude API呼び出しのパラメータ
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
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
              </CardContent>
            </Card>

            {/* Implementation Details */}
            <Card className="bg-gray-50">
              <CardHeader>
                <CardTitle>📚 実装詳細</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm text-gray-700">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">
                      コンテキスト圧縮の仕組み
                    </h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                      <li>
                        トークン数が閾値（80%）に達すると自動的に圧縮を実行
                      </li>
                      <li>古いメッセージをClaude自身が要約</li>
                      <li>最新10件のメッセージは要約せずそのまま保持</li>
                      <li>
                        要約結果をconversation_summaryタグでラップして挿入
                      </li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">
                      トークン推定方法
                    </h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                      <li>日本語: 1文字 ≈ 0.4トークン</li>
                      <li>英語: 1文字 ≈ 0.25トークン</li>
                      <li>平均: 1文字 ≈ 0.35トークン（日英混在を考慮）</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">
                      実装ファイル
                    </h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-600 font-mono text-xs">
                      <li>
                        projects/nakamura-misaki/src/infrastructure/context_manager.py
                      </li>
                      <li>
                        projects/nakamura-misaki/src/infrastructure/config.py
                      </li>
                      <li>
                        projects/nakamura-misaki/src/contexts/conversations/domain/services/claude_agent_service.py
                      </li>
                    </ul>
                  </div>
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                    <h3 className="font-medium text-blue-900 mb-2">
                      今後の拡張案
                    </h3>
                    <ul className="list-disc list-inside space-y-1 text-blue-700 text-sm">
                      <li>設定変更API実装（POST /api/context/settings）</li>
                      <li>トークン使用量の可視化グラフ</li>
                      <li>圧縮履歴の表示</li>
                      <li>Prompt Caching設定（コスト90%削減）</li>
                      <li>モデル選択（Sonnet/Haiku切り替え）</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
