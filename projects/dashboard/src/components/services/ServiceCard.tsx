/**
 * 🚀 NEW SIMPLIFIED ServiceCard Component
 * Direct external links only - no complex proxy logic
 */

'use client';

import { ExternalLink, BookOpen, Sparkles, Info } from 'lucide-react';
import { Service } from '@/config/services';
import Link from 'next/link';

interface ServiceCardProps {
  service: Service;
}

export function ServiceCard({ service }: ServiceCardProps) {
  const isInternal = service.url === '/' || service.id === 'dashboard';

  return (
    <div className="group block p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 hover:scale-105 border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600"
      data-testid={`service-card-${service.id}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <span
            className="text-3xl mr-3"
            role="img"
            aria-label={service.name}
          >
            {service.icon}
          </span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {service.name}
            </h3>
            {/* Category Badge */}
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 mt-1">
              {service.category}
            </span>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
        {service.description}
      </p>

      {/* Features */}
      {service.features && service.features.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center gap-1 mb-2">
            <Sparkles className="w-4 h-4 text-yellow-500" />
            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">主な機能</span>
          </div>
          <ul className="space-y-1">
            {service.features.slice(0, 3).map((feature, index) => (
              <li key={index} className="text-xs text-gray-600 dark:text-gray-400 flex items-start">
                <span className="mr-1">•</span>
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mb-3 flex gap-2">
        <Link
          href={`/service/${service.id}`}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30 rounded-md hover:bg-green-100 dark:hover:bg-green-900/50 transition-colors"
        >
          <Info className="w-3.5 h-3.5" />
          詳細・使い方
        </Link>

        <a
          href={service.url}
          target={isInternal ? '_self' : '_blank'}
          rel={isInternal ? undefined : 'noopener noreferrer'}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 rounded-md hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          開く
        </a>
      </div>

      {/* Tags */}
      {service.tags && service.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {service.tags.slice(0, 3).map(tag => (
            <span
              key={tag}
              className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
            >
              {tag}
            </span>
          ))}
          {service.tags.length > 3 && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              +{service.tags.length - 3} more
            </span>
          )}
        </div>
      )}

      {/* Footer - URL Display */}
      <div className="flex items-center justify-between text-xs border-t border-gray-100 dark:border-gray-700 pt-3">
        <span className="text-gray-500 dark:text-gray-400 truncate flex-1 mr-2">
          {service.url}
        </span>
        {service.status && service.status !== 'active' && (
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            service.status === 'maintenance'
              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
              : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
          }`}>
            {service.status}
          </span>
        )}
      </div>
    </div>
  );
}

export default ServiceCard;