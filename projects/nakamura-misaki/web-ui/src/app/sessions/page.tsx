'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { sessionApi, Session } from '@/lib/api';

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await sessionApi.list();
      setSessions(data);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
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
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6 sm:mb-8">セッション一覧</h1>

        <Card>
          <CardHeader>
            <CardTitle>全セッション ({sessions.length}件)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  className="border rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex flex-col sm:flex-row sm:justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium">{session.title}</h3>
                        {session.is_active && (
                          <Badge variant="default">Active</Badge>
                        )}
                      </div>
                      <div className="mt-2 text-sm text-gray-600 space-y-1">
                        <div>ユーザー: {session.user_id}</div>
                        <div>メッセージ数: {session.message_count}件</div>
                        <div className="font-mono text-xs text-gray-400 break-all">
                          ID: {session.session_id}
                        </div>
                      </div>
                    </div>
                    <div className="text-left sm:text-right text-sm text-gray-500">
                      <div>
                        作成: {new Date(session.created_at).toLocaleDateString('ja-JP')}
                      </div>
                      <div>
                        最終: {new Date(session.last_active).toLocaleString('ja-JP')}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
