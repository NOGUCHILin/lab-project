import { exec as _exec } from 'child_process';
import { promisify } from 'util';
import { readFile } from 'fs/promises';

const exec = promisify(_exec);

export type Metrics = {
  ts: number;
  cpu: { usage: number };
  mem: { total: number; used: number; free: number; usage: number };
  disk: { total: number; used: number; free: number; usage: number; mount: string };
};

let prevTotal = 0;
let prevIdle = 0;

async function readProcStat(): Promise<{ total: number; idle: number }> {
  const text = await readFile('/proc/stat', 'utf8');
  const line = text.split('\n').find(l => l.startsWith('cpu '));
  if (!line) return { total: 0, idle: 0 };
  const parts = line.trim().split(/\s+/).slice(1).map(Number);
  // user nice system idle iowait irq softirq steal guest guest_nice
  const idle = (parts[3] || 0) + (parts[4] || 0);
  const total = parts.reduce((a, b) => a + (b || 0), 0);
  return { total, idle };
}

async function cpuUsage(): Promise<number> {
  const { total, idle } = await readProcStat();
  if (prevTotal === 0) {
    prevTotal = total; prevIdle = idle;
    return 0;
  }
  const dTotal = total - prevTotal;
  const dIdle = idle - prevIdle;
  prevTotal = total; prevIdle = idle;
  if (dTotal <= 0) return 0;
  const usage = (1 - dIdle / dTotal) * 100;
  return Math.max(0, Math.min(100, usage));
}

async function memUsage() {
  const text = await readFile('/proc/meminfo', 'utf8');
  const map = new Map<string, number>();
  for (const line of text.split('\n')) {
    const m = line.match(/^(\w+):\s+(\d+)/);
    if (m) map.set(m[1], parseInt(m[2], 10));
  }
  // Values in kB
  const totalKb = map.get('MemTotal') || 0;
  const availKb = map.get('MemAvailable') || 0;
  const usedKb = Math.max(0, totalKb - availKb);
  const usage = totalKb > 0 ? (usedKb / totalKb) * 100 : 0;
  return {
    total: totalKb * 1024,
    used: usedKb * 1024,
    free: availKb * 1024,
    usage: Math.max(0, Math.min(100, usage))
  };
}

async function diskUsage(mount: string = '/') {
  // Use df for simplicity (-B1 bytes, POSIX format)
  const { stdout } = await exec(`df -P -B1 ${mount}`);
  const lines = stdout.trim().split('\n');
  const data = lines[lines.length - 1].trim().split(/\s+/);
  // Filesystem Size Used Avail Use% Mounted on
  const total = parseInt(data[1], 10) || 0;
  const used = parseInt(data[2], 10) || 0;
  const free = parseInt(data[3], 10) || 0;
  const usage = total > 0 ? (used / total) * 100 : 0;
  return { total, used, free, usage: Math.max(0, Math.min(100, usage)), mount };
}

export async function getMetrics(): Promise<Metrics> {
  const [cpu, mem, disk] = await Promise.all([
    cpuUsage(),
    memUsage(),
    diskUsage('/'),
  ]);
  return {
    ts: Date.now(),
    cpu: { usage: Number(cpu.toFixed(1)) },
    mem: { ...mem, usage: Number(mem.usage.toFixed(1)) },
    disk: { ...disk, usage: Number(disk.usage.toFixed(1)) },
  };
}

