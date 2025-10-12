'use client';

import { useEffect } from 'react';
import { logError } from '@/lib/error-logger';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to backend
    logError(error, { digest: error.digest });
  }, [error]);

  return (
    <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
      <Card className="max-w-2xl w-full">
        <CardHeader>
          <CardTitle className="text-red-600">エラーが発生しました</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="font-mono text-sm text-red-800">{error.message}</p>
          </div>

          <div className="text-sm text-gray-600">
            <p>このエラーはログに記録されました。</p>
            <p>問題が解決しない場合は、管理者に連絡してください。</p>
          </div>

          <div className="flex gap-2">
            <Button onClick={reset}>再試行</Button>
            <Button variant="outline" onClick={() => window.location.href = '/'}>
              ダッシュボードに戻る
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
