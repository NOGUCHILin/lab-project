'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { errorLogApi, ErrorLog } from '@/lib/api';

export default function LogsPage() {
  const [errors, setErrors] = useState<ErrorLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedError, setSelectedError] = useState<ErrorLog | null>(null);

  useEffect(() => {
    fetchErrors();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchErrors, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchErrors = async () => {
    try {
      const data = await errorLogApi.list();
      setErrors(data);
    } catch (error) {
      console.error('Failed to fetch error logs:', error);
    } finally {
      setLoading(false);
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
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6 sm:mb-8">フロントエンドエラーログ</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {/* エラー一覧 */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>エラー一覧 ({errors.length}件)</CardTitle>
                <button
                  onClick={fetchErrors}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  🔄 更新
                </button>
              </div>
            </CardHeader>
            <CardContent>
              {errors.length === 0 ? (
                <p className="text-gray-500">エラーはありません</p>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {errors.map((error) => (
                    <div
                      key={error.id}
                      onClick={() => setSelectedError(error)}
                      className={`border rounded-lg p-3 cursor-pointer hover:bg-gray-50 ${
                        selectedError?.id === error.id ? 'bg-blue-50 border-blue-300' : ''
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <div className="flex gap-2">
                          <Badge variant="destructive">Error</Badge>
                          {error.occurrence_count > 1 && (
                            <Badge variant="secondary">{error.occurrence_count}回</Badge>
                          )}
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(error.last_seen).toLocaleString('ja-JP')}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-red-700 truncate">
                        {error.message}
                      </p>
                      {error.url && (
                        <p className="text-xs text-gray-500 truncate mt-1">
                          {error.url}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* エラー詳細 */}
          <Card>
            <CardHeader>
              <CardTitle>エラー詳細</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedError ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">発生回数</h3>
                    <p className="text-sm">
                      <span className="text-2xl font-bold text-red-600">{selectedError.occurrence_count}</span> 回
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">最初の発生</h3>
                    <p className="text-sm">
                      {new Date(selectedError.first_seen).toLocaleString('ja-JP')}
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">最後の発生</h3>
                    <p className="text-sm">
                      {new Date(selectedError.last_seen).toLocaleString('ja-JP')}
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">エラーメッセージ</h3>
                    <p className="text-sm text-red-700 bg-red-50 p-2 rounded">
                      {selectedError.message}
                    </p>
                  </div>

                  {selectedError.url && (
                    <div>
                      <h3 className="font-semibold text-sm text-gray-700 mb-2">URL</h3>
                      <p className="text-sm font-mono break-all">{selectedError.url}</p>
                    </div>
                  )}

                  {selectedError.stack && (
                    <div>
                      <h3 className="font-semibold text-sm text-gray-700 mb-2">スタックトレース</h3>
                      <pre className="text-xs bg-gray-900 text-gray-100 p-3 rounded overflow-x-auto">
                        {selectedError.stack}
                      </pre>
                    </div>
                  )}

                  {selectedError.user_agent && (
                    <div>
                      <h3 className="font-semibold text-sm text-gray-700 mb-2">User Agent</h3>
                      <p className="text-xs font-mono break-all text-gray-600">
                        {selectedError.user_agent}
                      </p>
                    </div>
                  )}

                  {selectedError.context && (
                    <div>
                      <h3 className="font-semibold text-sm text-gray-700 mb-2">追加情報</h3>
                      <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                        {JSON.stringify(selectedError.context, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">左からエラーを選択してください</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
