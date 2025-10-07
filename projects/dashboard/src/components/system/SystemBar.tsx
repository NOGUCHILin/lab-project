'use client';

import { useEffect, useState } from 'react';

type Metrics = {
  ts: number;
  cpu: { usage: number };
  mem: { usage: number };
  disk: { usage: number };
};

function formatPct(n: number) {
  return `${n.toFixed(0)}%`;
}

export default function SystemBar() {
  const [m, setM] = useState<Metrics | null>(null);

  useEffect(() => {
    const es = new EventSource('/api/system/metrics/stream');
    es.onmessage = (ev) => {
      try { setM(JSON.parse(ev.data)); } catch {}
    };
    return () => es.close();
  }, []);

  const cpu = m?.cpu.usage ?? 0;
  const mem = m?.mem.usage ?? 0;
  const disk = m?.disk.usage ?? 0;

  const Item = ({ label, value, color }: { label: string; value: number; color: string }) => (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-800 border border-gray-700">
      <span className="text-xs text-gray-300 w-10">{label}</span>
      <div className="w-28 h-2 bg-gray-700 rounded">
        <div className="h-2 rounded" style={{ width: `${Math.min(100, Math.max(0, value)).toFixed(0)}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs text-gray-200 w-10 text-right">{formatPct(value)}</span>
    </div>
  );

  return (
    <div className="fixed bottom-4 right-4 flex gap-2 z-50">
      <Item label="CPU" value={cpu} color="#60a5fa" />
      <Item label="MEM" value={mem} color="#34d399" />
      <Item label="DISK" value={disk} color="#f59e0b" />
    </div>
  );
}

