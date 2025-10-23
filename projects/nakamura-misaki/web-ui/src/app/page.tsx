'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { taskApi, userApi, sessionApi, errorLogApi, Task, User, Session } from '@/lib/api';

// Dashboard - Nakamura-Misaki Web UI v2.0
export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [errorCount, setErrorCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tasksData, usersData, sessionsData, errorLogs] = await Promise.all([
          taskApi.list(),
          userApi.list(),
          sessionApi.list(),
          errorLogApi.list(10),
        ]);
        setTasks(tasksData);
        setUsers(usersData);
        setSessions(sessionsData);
        setErrorCount(errorLogs.length);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const todayTasks = tasks.filter((task) => {
    const dueDate = new Date(task.due_date);
    const today = new Date();
    return dueDate.toDateString() === today.toDateString();
  });

  const overdueTasks = tasks.filter((task) => {
    const dueDate = new Date(task.due_date);
    return dueDate < new Date() && task.status !== 'completed';
  });

  const activeSessions = sessions.filter((s) => s.is_active);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">nakamura-misaki 管理画面</h1>

        {/* メトリクスカード */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Link href="/tasks">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">今日のタスク</CardTitle>
                <span className="text-2xl">📋</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{todayTasks.length}</div>
                <p className="text-xs text-muted-foreground">本日期限のタスク</p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/tasks">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">期限切れ</CardTitle>
                <span className="text-2xl">⚠️</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{overdueTasks.length}</div>
                <p className="text-xs text-muted-foreground">期限切れタスク</p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/users">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">アクティブユーザー</CardTitle>
                <span className="text-2xl">👤</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{users.length}</div>
                <p className="text-xs text-muted-foreground">登録ユーザー数</p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/sessions">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">セッション</CardTitle>
                <span className="text-2xl">💬</span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{activeSessions.length}</div>
                <p className="text-xs text-muted-foreground">アクティブセッション</p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/logs">
            <Card className={`hover:shadow-md transition-shadow cursor-pointer ${errorCount > 0 ? 'border-red-200' : ''}`}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">エラーログ</CardTitle>
                <span className="text-2xl">🔴</span>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${errorCount > 0 ? 'text-red-600' : ''}`}>{errorCount}</div>
                <p className="text-xs text-muted-foreground">最近10件のエラー</p>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* 今日のタスク */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>今日のタスク</CardTitle>
          </CardHeader>
          <CardContent>
            {todayTasks.length === 0 ? (
              <p className="text-muted-foreground">今日のタスクはありません</p>
            ) : (
              <div className="space-y-4">
                {todayTasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between border-b pb-3">
                    <div>
                      <h3 className="font-medium">{task.title}</h3>
                      <p className="text-sm text-muted-foreground">{task.description}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={task.status === 'completed' ? 'default' : 'secondary'}>
                        {getStatusText(task.status)}
                      </Badge>
                      <span className="text-sm">{task.progress}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 期限切れタスク */}
        {overdueTasks.length > 0 && (
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="text-red-600">期限切れタスク</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {overdueTasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between border-b pb-3">
                    <div>
                      <h3 className="font-medium">{task.title}</h3>
                      <p className="text-sm text-red-600">
                        期限: {new Date(task.due_date).toLocaleString('ja-JP')}
                      </p>
                    </div>
                    <Badge variant="destructive">{getStatusText(task.status)}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    pending: '未着手',
    in_progress: '進行中',
    completed: '完了',
    cancelled: 'キャンセル',
  };
  return statusMap[status] || status;
}
