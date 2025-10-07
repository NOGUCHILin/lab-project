export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

import { getMetrics } from '@/lib/system/metrics';

export async function GET() {
  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();
      let alive = true;

      async function push() {
        try {
          const m = await getMetrics();
          const payload = `data: ${JSON.stringify(m)}\n\n`;
          controller.enqueue(encoder.encode(payload));
        } catch (e) {
          controller.enqueue(encoder.encode(`event: error\n`));
        }
      }

      // Send an initial comment to open the stream
      controller.enqueue(encoder.encode(`: ok\n\n`));
      const id = setInterval(() => alive && push(), 1000);
      // First sample ASAP
      push();

      const close = () => {
        alive = false;
        clearInterval(id);
        try { controller.close(); } catch {}
      };
      // @ts-ignore
      (globalThis as any).addEventListener?.('close', close);
    },
    cancel() {},
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      Connection: 'keep-alive',
    },
  });
}

