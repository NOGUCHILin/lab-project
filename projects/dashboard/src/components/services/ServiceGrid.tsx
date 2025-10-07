/**
 * 🚀 NEW SIMPLIFIED ServiceGrid Component
 * No complex state management, just pure display logic
 */

'use client';

import { useState, useMemo } from 'react';
import { Service } from '@/config/services';
import { ServiceCard } from './ServiceCard';

interface ServiceGridProps {
  services: Service[];
  columns?: 1 | 2 | 3 | 4;
}

export function ServiceGrid({ services, columns = 3 }: ServiceGridProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Filter services based on search and category
  const filteredServices = useMemo(() => {
    let filtered = services;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(service => service.category === selectedCategory);
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(service =>
        service.name.toLowerCase().includes(term) ||
        service.description.toLowerCase().includes(term) ||
        service.tags?.some(tag => tag.toLowerCase().includes(term))
      );
    }

    return filtered;
  }, [services, searchTerm, selectedCategory]);

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set<string>();
    services.forEach(service => cats.add(service.category));
    return Array.from(cats).sort();
  }, [services]);

  // Grid column classes
  const getGridClass = () => {
    switch (columns) {
      case 1: return 'grid-cols-1';
      case 2: return 'grid-cols-1 md:grid-cols-2';
      case 3: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
      case 4: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';
      default: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
    }
  };

  // Category stats
  const categoryStats = useMemo(() => {
    const stats = new Map<string, number>();
    services.forEach(service => {
      stats.set(service.category, (stats.get(service.category) || 0) + 1);
    });
    return stats;
  }, [services]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">サービス一覧</h2>
          <p className="text-sm text-gray-400 mt-1">
            {services.length} サービス
            {filteredServices.length !== services.length && (
              <span className="text-blue-400"> • {filteredServices.length} 表示中</span>
            )}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1">
          <input
            type="text"
            placeholder="サービス、説明、タグで検索..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Category Filter */}
        {categories.length > 1 && (
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            <option value="all">
              全カテゴリ ({services.length})
            </option>
            {categories.map(category => (
              <option key={category} value={category}>
                {category} ({categoryStats.get(category) || 0})
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Services Grid */}
      {filteredServices.length > 0 ? (
        <div className={`grid ${getGridClass()} gap-6`}>
          {filteredServices.map(service => (
            <ServiceCard key={service.id} service={service} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-white mb-2">サービスが見つかりません</h3>
          <p className="text-gray-400">
            {searchTerm ? (
              <>
                「<span className="text-blue-400">{searchTerm}</span>」に一致するサービスがありません
              </>
            ) : (
              '選択したカテゴリにサービスがありません'
            )}
          </p>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              検索をクリア
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default ServiceGrid;