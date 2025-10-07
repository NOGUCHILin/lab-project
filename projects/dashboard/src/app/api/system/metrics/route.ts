export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { getMetrics } from '@/lib/system/metrics';

export async function GET() {
  try {
    const m = await getMetrics();
    return NextResponse.json(m, { headers: { 'Cache-Control': 'no-store' } });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'metrics failed' }, { status: 500 });
  }
}

