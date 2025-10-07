/**
 * 🚀 SIMPLE Health Indicator Component
 * Optional health status display
 */

'use client';

import { Activity, CheckCircle2, XCircle, HelpCircle } from 'lucide-react';
import { useHealthCheck, HealthStatus } from '@/hooks/useHealthCheck';

interface HealthIndicatorProps {
  url?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  enabled?: boolean;
}

export function HealthIndicator({
  url,
  size = 'sm',
  showLabel = false,
  enabled = true
}: HealthIndicatorProps) {
  const status = useHealthCheck(url, { enabled });

  const getStatusConfig = (status: HealthStatus) => {
    switch (status) {
      case 'online':
        return {
          icon: CheckCircle2,
          color: 'text-green-500',
          bgColor: 'bg-green-500',
          label: 'Online'
        };
      case 'offline':
        return {
          icon: XCircle,
          color: 'text-red-500',
          bgColor: 'bg-red-500',
          label: 'Offline'
        };
      case 'checking':
        return {
          icon: Activity,
          color: 'text-blue-500',
          bgColor: 'bg-blue-500',
          label: 'Checking...'
        };
      default:
        return {
          icon: HelpCircle,
          color: 'text-gray-400',
          bgColor: 'bg-gray-400',
          label: 'Unknown'
        };
    }
  };

  const config = getStatusConfig(status);
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  const dotSizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  if (!enabled || !url) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      {/* Icon version for 'checking' status */}
      {status === 'checking' ? (
        <Icon
          className={`${sizeClasses[size]} ${config.color} animate-pulse`}
        />
      ) : (
        /* Dot version for other statuses */
        <div
          className={`${dotSizeClasses[size]} ${config.bgColor} rounded-full ${
            status === 'online' ? 'animate-pulse' : ''
          }`}
        />
      )}

      {/* Optional label */}
      {showLabel && (
        <span className={`${textSizeClasses[size]} ${config.color} font-medium`}>
          {config.label}
        </span>
      )}
    </div>
  );
}

export default HealthIndicator;