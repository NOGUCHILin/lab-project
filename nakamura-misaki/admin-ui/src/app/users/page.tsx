'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { userApi, User } from '@/lib/api';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const data = await userApi.list();
      setUsers(data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">ユーザー一覧</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {users.map((user) => (
            <Card key={user.user_id}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">
                    {user.display_name || user.real_name || user.name || user.user_id}
                  </span>
                  {user.is_admin && <Badge>Admin</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-500">User ID:</span>
                    <div className="font-mono text-xs">{user.user_id}</div>
                  </div>
                  {user.email && (
                    <div>
                      <span className="text-gray-500">Email:</span>
                      <div>{user.email}</div>
                    </div>
                  )}
                  {user.real_name && (
                    <div>
                      <span className="text-gray-500">Real Name:</span>
                      <div>{user.real_name}</div>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-500">登録日:</span>
                    <div>{new Date(user.created_at).toLocaleDateString('ja-JP')}</div>
                  </div>
                  <div className="pt-2 flex gap-2">
                    {user.is_bot && <Badge variant="secondary">Bot</Badge>}
                    {!user.is_admin && !user.is_bot && <Badge variant="outline">User</Badge>}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
