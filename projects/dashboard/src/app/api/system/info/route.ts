import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function GET() {
  try {
    const systemInfo = {
      timestamp: new Date().toISOString(),
      hostname: process.env.HOSTNAME || 'unknown',
      nodeEnv: process.env.NODE_ENV,
      port: process.env.PORT,
      
      // プロセス情報
      processInfo: {
        pid: process.pid,
        version: process.version,
        platform: process.platform,
        arch: process.arch,
        uptime: Math.floor(process.uptime()),
        memory: process.memoryUsage(),
        relatedProcesses: [] as string[]
      },

      // サービス情報
      services: {
        dashboard: {
          port: process.env.PORT || '3005',
          url: `http://localhost:${process.env.PORT || '3005'}`,
          proxyUrls: {
            code: `https://home-lab-01.tail4ed625.ts.net:8443/`,
            voice: `https://home-lab-01.tail4ed625.ts.net:8891/`,
            syncthing: `https://home-lab-01.tail4ed625.ts.net:10000/`
          }
        },
        targets: {
          codeServer: 'http://127.0.0.1:8889',
          openaiRealtime: 'http://127.0.0.1:8891',
          syncthing: 'http://127.0.0.1:8384'
        }
      },

      // ネットワーク情報
      network: {
        uptime: undefined as string | undefined,
        listeningPorts: [] as string[]
      },
      
      // プロキシ設定状況
      proxyConfig: {
        allowedServices: ['code', 'voice', 'syncthing'],
        voiceAllowedPaths: [
          '^/$',
          '^/api/',
          '^/static/',
          '^/realtime\\.js$',
          '^/health$'
        ]
      }
    };

    // 追加のシステム情報を取得
    try {
      const { stdout: hostname } = await execAsync('hostname');
      systemInfo.hostname = hostname.trim();
    } catch (e) {
      // ignore
    }

    try {
      const { stdout: uptime } = await execAsync('uptime');
      systemInfo.network.uptime = uptime.trim();
    } catch (e) {
      // ignore  
    }

    try {
      const { stdout: ps } = await execAsync('ps aux | grep -E "(npm|next|node)" | grep -v grep');
      systemInfo.processInfo.relatedProcesses = ps.trim().split('\n').slice(0, 10);
    } catch (e) {
      systemInfo.processInfo.relatedProcesses = [];
    }

    try {
      const { stdout: netstat } = await execAsync('ss -tuln | grep -E "(3005|8889|8891|8384)"');
      systemInfo.network.listeningPorts = netstat.trim().split('\n');
    } catch (e) {
      systemInfo.network.listeningPorts = [];
    }

    return NextResponse.json(systemInfo);
  } catch (error) {
    return NextResponse.json({
      error: 'Failed to get system info',
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}