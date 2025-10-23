'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { promptApi, Prompt } from '@/lib/api';

export default function PromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

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
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6 sm:mb-8">プロンプト編集</h1>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6">
          {/* プロンプト一覧 */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>プロンプト一覧</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {prompts.map((prompt) => (
                  <button
                    key={prompt.name}
                    onClick={() => {
                      setSelectedPrompt(prompt);
                      setEditing(false);
                    }}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                      selectedPrompt?.name === prompt.name
                        ? 'bg-blue-100 text-blue-900'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <div className="font-medium">{prompt.name}</div>
                    <div className="text-xs text-gray-500">{prompt.version}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* プロンプト編集エリア */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>
                  {selectedPrompt?.name || 'プロンプト未選択'}
                </CardTitle>
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
                      className="mt-1 font-mono"
                      rows={20}
                    />
                  </div>

                  <div className="text-sm text-gray-500">
                    <div>作成日時: {new Date(selectedPrompt.created_at).toLocaleString('ja-JP')}</div>
                    <div>更新日時: {new Date(selectedPrompt.updated_at).toLocaleString('ja-JP')}</div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">左からプロンプトを選択してください</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
