export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { getMetrics } from '@/lib/system/metrics';

export async function GET() {
  try {
    const m = await getMetrics();
    return NextResponse.json(m, { headers: { 'Cache-Control': 'no-store' } });
  } catch (e: unknown) {
    const errorMessage = e instanceof Error ? e.message : 'metrics failed';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}

