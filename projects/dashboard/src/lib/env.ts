/**
 * Environment configuration with type safety
 * All environment variables used in the application should be defined here
 */

// Type-safe environment configuration
export interface EnvConfig {
  // Base Configuration
  BASE_URL: string;
  DASHBOARD_PORT: number;

  // Service Ports
  CODE_SERVER_PORT: number;
  SYNCTHING_PORT: number;
  FILE_MANAGER_PORT: number;
  NATS_PORT: number;
  GPT_REALTIME_PORT: number;

  // Feature Flags
  ENABLE_HEALTH_CHECK: boolean;
  HEALTH_CHECK_INTERVAL: number;
  HEALTH_CHECK_TIMEOUT: number;

  // Environment
  ENV: 'development' | 'production' | 'test';
}

/**
 * Get environment configuration with defaults
 */
export function getEnvConfig(): EnvConfig {
  return {
    // Base Configuration
    BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost',
    DASHBOARD_PORT: parseInt(process.env.NEXT_PUBLIC_DASHBOARD_PORT || '3005'),

    // Service Ports
    CODE_SERVER_PORT: parseInt(process.env.NEXT_PUBLIC_CODE_SERVER_PORT || '8889'),
    SYNCTHING_PORT: parseInt(process.env.NEXT_PUBLIC_SYNCTHING_PORT || '8384'),
    FILE_MANAGER_PORT: parseInt(process.env.NEXT_PUBLIC_FILE_MANAGER_PORT || '9000'),
    NATS_PORT: parseInt(process.env.NEXT_PUBLIC_NATS_PORT || '8222'),
    GPT_REALTIME_PORT: parseInt(process.env.NEXT_PUBLIC_GPT_REALTIME_PORT || '8000'),

    // Feature Flags
    ENABLE_HEALTH_CHECK: process.env.NEXT_PUBLIC_ENABLE_HEALTH_CHECK === 'true',
    HEALTH_CHECK_INTERVAL: parseInt(process.env.NEXT_PUBLIC_HEALTH_CHECK_INTERVAL || '30000'),
    HEALTH_CHECK_TIMEOUT: parseInt(process.env.NEXT_PUBLIC_HEALTH_CHECK_TIMEOUT || '5000'),

    // Environment
    ENV: (process.env.NEXT_PUBLIC_ENV || 'development') as 'development' | 'production' | 'test',
  };
}

// Export singleton instance
export const env = getEnvConfig();