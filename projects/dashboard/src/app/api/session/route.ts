/**
 * OpenAI Realtime用のセッション管理API
 * realtime.jsが期待する/api/sessionエンドポイントを提供
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // realtime.jsからのセッション開始リクエストを処理
    let body = {};
    try {
      const text = await request.text();
      console.log('Raw request body:', text);
      if (text.trim()) {
        body = JSON.parse(text);
      }
    } catch (parseError) {
      console.log('Body parse error (using empty object):', parseError);
      body = {};
    }
    console.log('Session request received:', body);
    
    // OpenAI Realtime APIからephemeral tokenを取得
    const openaiApiKey = process.env.OPENAI_API_KEY;
    if (!openaiApiKey) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      );
    }

    // OpenAI Realtime Sessions APIを呼び出し
    const openaiResponse = await fetch('https://api.openai.com/v1/realtime/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-realtime-preview',
        modalities: ['audio', 'text'],
        instructions: 'You are a helpful assistant.',
        voice: 'alloy',
        input_audio_format: 'pcm16',
        output_audio_format: 'pcm16',
        turn_detection: {
          type: 'server_vad',
          threshold: 0.5,
          prefix_padding_ms: 300,
          silence_duration_ms: 200
        }
      })
    });

    if (!openaiResponse.ok) {
      const errorData = await openaiResponse.text();
      console.error('OpenAI API error:', openaiResponse.status, errorData);
      return NextResponse.json(
        { error: 'Failed to create OpenAI session', details: errorData },
        { status: openaiResponse.status }
      );
    }

    const sessionData = await openaiResponse.json();
    
    return NextResponse.json(sessionData);
  } catch (error) {
    console.error('Session API error:', error);
    return NextResponse.json(
      { error: 'Failed to create session', message: error instanceof Error ? error.message : 'Unknown error' }, 
      { status: 500 }
    );
  }
}

export async function GET() {
  // セッション状態の確認用
  return NextResponse.json({
    status: 'available',
    timestamp: new Date().toISOString()
  });
}