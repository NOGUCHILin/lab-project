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

export default function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // 現在適用中のプロンプト名（将来的にAPIから取得）
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

  // プロンプト分析結果をメモ化
  const analysis = useMemo(
    () => (selectedPrompt ? analyzePrompt(selectedPrompt.system_prompt) : null),
    [selectedPrompt?.system_prompt]
  );

  const cachingInfo = useMemo(
    () => (analysis ? getCachingRecommendations(analysis.tokenCount) : null),
    [analysis?.tokenCount]
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
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
            プロンプト編集
          </h1>
          <p className="text-sm text-gray-600 mt-2">
            Anthropic Context Engineering Principles 準拠
          </p>
        </div>

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
      </div>
    </div>
  );
}
