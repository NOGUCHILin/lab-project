/**
 * サーバーサイドAPIルート: NixOSレジストリからサービス一覧を取得
 * /etc/unified-dashboard/services.jsonを読み込み、クライアントに返す
 */

import { NextResponse } from 'next/server';
import fs from 'fs';

interface NixOSServiceRegistry {
  [key: string]: {
    name: string;
    description: string;
    icon: string;
    port: number;
    path: string;
    url: string;
    apiUrl: string;
    healthCheck: string;
  };
}

export async function GET() {
  const servicesPath = process.env.SERVICES_CONFIG || '/etc/unified-dashboard/services.json';

  try {
    const rawData = fs.readFileSync(servicesPath, 'utf-8');
    const registry: NixOSServiceRegistry = JSON.parse(rawData);

    return NextResponse.json(registry);
  } catch (error) {
    console.error('Failed to load services from NixOS registry:', error);
    return NextResponse.json({}, { status: 500 });
  }
}
