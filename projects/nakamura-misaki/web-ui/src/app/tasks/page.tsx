'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { taskApi, Task } from '@/lib/api';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const data = await taskApi.list();
      setTasks(data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
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
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6 sm:mb-8">タスク管理</h1>

        <Card>
          <CardHeader>
            <CardTitle>全タスク一覧</CardTitle>
          </CardHeader>
          <CardContent>
            {tasks.length === 0 ? (
              <p className="text-gray-500">タスクがありません</p>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="border rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex flex-col sm:flex-row sm:justify-between gap-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{task.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {task.description}
                        </p>
                        <div className="mt-2 text-sm text-gray-500 flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-0">
                          <span>ユーザー: {task.user_id}</span>
                          <span className="hidden sm:inline mx-2">•</span>
                          <span>
                            期限: {new Date(task.due_date).toLocaleString('ja-JP')}
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-row sm:flex-col items-start sm:items-end gap-2">
                        <Badge
                          variant={
                            task.status === 'completed'
                              ? 'default'
                              : task.status === 'in_progress'
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          {getStatusText(task.status)}
                        </Badge>
                        <span className="text-sm font-medium">
                          進捗: {task.progress}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
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
