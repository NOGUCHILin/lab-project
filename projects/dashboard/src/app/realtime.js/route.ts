/**
 * OpenAI Realtime用のrealtime.jsファイル直接配信
 * HTMLから絶対パス /realtime.js でアクセスされるため
 */

export async function GET() {
  try {
    // OpenAI Realtimeサービスから直接realtime.jsを取得
    const response = await fetch('http://127.0.0.1:8891/realtime.js');
    
    if (!response.ok) {
      return new Response('File not found', { status: 404 });
    }
    
    const content = await response.text();
    
    return new Response(content, {
      headers: {
        'Content-Type': 'application/javascript; charset=UTF-8',
        'Cache-Control': 'public, max-age=300', // 5分間キャッシュ
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (error) {
    console.error('Failed to fetch realtime.js:', error);
    return new Response('Service unavailable', { status: 502 });
  }
}