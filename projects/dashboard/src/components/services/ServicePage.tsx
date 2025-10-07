'use client';

import { ArrowLeft, ExternalLink, BookOpen, Sparkles, Activity, CheckCircle, AlertCircle, ChevronDown, ChevronRight, Terminal, Settings, Globe, Users, HelpCircle, Wrench, Zap, FileText } from 'lucide-react';
import { Service } from '@/config/services';
import { getServiceDetail } from '@/config/serviceDetails';
import Link from 'next/link';
import { useState } from 'react';

interface ServicePageProps {
  service: Service;
}

export function ServicePage({ service }: ServicePageProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    quickStart: true,
    features: true,
    useCases: false,
    faq: false,
    troubleshooting: false,
    shortcuts: false,
    apiEndpoints: false,
    configuration: false,
    integrations: false,
    resources: true
  });

  const isInternal = service.url === '/' || service.id === 'dashboard';
  const serviceDetail = getServiceDetail(service.id);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const SectionHeader = ({ title, icon: Icon, section, count }: { title: string; icon: any; section: string; count?: number }) => (
    <button
      onClick={() => toggleSection(section)}
      className="flex items-center justify-between w-full p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
    >
      <div className="flex items-center gap-3">
        <Icon className="w-5 h-5 text-blue-500" />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          {title}
          {count !== undefined && (
            <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">({count})</span>
          )}
        </h2>
      </div>
      {expandedSections[section] ? (
        <ChevronDown className="w-5 h-5 text-gray-500" />
      ) : (
        <ChevronRight className="w-5 h-5 text-gray-500" />
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            ダッシュボードに戻る
          </Link>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
            <div className="flex items-start gap-6">
              <span className="text-6xl" role="img" aria-label={service.name}>
                {service.icon}
              </span>
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {service.name}
                </h1>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 mb-4">
                  {service.category}
                </span>
                <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
                  {service.description}
                </p>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <a
                    href={service.url}
                    target={isInternal ? '_self' : '_blank'}
                    rel={isInternal ? undefined : 'noopener noreferrer'}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                  >
                    <Activity className="w-4 h-4" />
                    サービスを開く
                    {!isInternal && <ExternalLink className="w-4 h-4" />}
                  </a>

                  {service.docsUrl && (
                    <a
                      href={service.docsUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition-colors"
                    >
                      <BookOpen className="w-4 h-4" />
                      公式ドキュメント
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {serviceDetail ? (
          <>
            {/* Quick Start Section */}
            {serviceDetail.quickStart && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title={serviceDetail.quickStart.title} icon={Zap} section="quickStart" />
                {expandedSections.quickStart && (
                  <div className="p-6 pt-0">
                    <div className="space-y-4">
                      {serviceDetail.quickStart.steps.map((step) => (
                        <div key={step.step} className="flex gap-4">
                          <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                            {step.step}
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                              {step.title}
                            </h3>
                            <p className="text-gray-600 dark:text-gray-300 mb-2">
                              {step.description}
                            </p>
                            {step.tip && (
                              <p className="text-sm text-blue-600 dark:text-blue-400 mb-2">
                                💡 {step.tip}
                              </p>
                            )}
                            {step.command && (
                              <code className="block p-2 bg-gray-100 dark:bg-gray-700 rounded text-sm text-gray-800 dark:text-gray-200">
                                {step.command}
                              </code>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Features Section */}
            {serviceDetail.features && serviceDetail.features.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="主な機能" icon={Sparkles} section="features" count={serviceDetail.features.length} />
                {expandedSections.features && (
                  <div className="p-6 pt-0">
                    <div className="grid md:grid-cols-2 gap-4">
                      {serviceDetail.features.map((feature, index) => (
                        <div
                          key={index}
                          className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                        >
                          <div className="flex items-start gap-3">
                            {feature.icon && (
                              <span className="text-2xl flex-shrink-0">{feature.icon}</span>
                            )}
                            <div>
                              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                                {feature.name}
                              </h3>
                              <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                                {feature.description}
                              </p>
                              <p className="text-sm text-gray-700 dark:text-gray-200 mb-2">
                                <strong>使い方:</strong> {feature.howToUse}
                              </p>
                              {feature.example && (
                                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                                  例: {feature.example}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Use Cases Section */}
            {serviceDetail.useCases && serviceDetail.useCases.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="活用事例" icon={FileText} section="useCases" count={serviceDetail.useCases.length} />
                {expandedSections.useCases && (
                  <div className="p-6 pt-0">
                    <div className="space-y-6">
                      {serviceDetail.useCases.map((useCase, index) => (
                        <div key={index} className="border-l-4 border-blue-500 pl-4">
                          <h3 className="font-semibold text-lg text-gray-900 dark:text-white mb-2">
                            {useCase.title}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300 mb-3">
                            {useCase.scenario}
                          </p>
                          <div className="mb-3">
                            <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">手順:</h4>
                            <ol className="list-decimal list-inside space-y-1">
                              {useCase.steps.map((step, stepIndex) => (
                                <li key={stepIndex} className="text-gray-600 dark:text-gray-300">
                                  {step}
                                </li>
                              ))}
                            </ol>
                          </div>
                          {useCase.benefits && (
                            <div>
                              <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">メリット:</h4>
                              <div className="flex flex-wrap gap-2">
                                {useCase.benefits.map((benefit, benefitIndex) => (
                                  <span
                                    key={benefitIndex}
                                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200"
                                  >
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    {benefit}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* API Endpoints Section */}
            {serviceDetail.apiEndpoints && serviceDetail.apiEndpoints.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="APIエンドポイント" icon={Globe} section="apiEndpoints" count={serviceDetail.apiEndpoints.length} />
                {expandedSections.apiEndpoints && (
                  <div className="p-6 pt-0">
                    <div className="space-y-4">
                      {serviceDetail.apiEndpoints.map((endpoint, index) => (
                        <div key={index} className="border dark:border-gray-700 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                endpoint.method === 'GET' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                                endpoint.method === 'POST' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' :
                                endpoint.method === 'WebSocket' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' :
                                'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                              }`}>
                                {endpoint.method}
                              </span>
                              <code className="text-sm font-mono text-gray-800 dark:text-gray-200">
                                {endpoint.endpoint}
                              </code>
                            </div>
                            {endpoint.auth && (
                              <span className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded">
                                認証必須
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                            {endpoint.description}
                          </p>
                          {endpoint.example && (
                            <code className="block p-2 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-800 dark:text-gray-200 overflow-x-auto">
                              {endpoint.example}
                            </code>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Configuration Section */}
            {serviceDetail.configuration && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="設定情報" icon={Settings} section="configuration" />
                {expandedSections.configuration && (
                  <div className="p-6 pt-0">
                    {serviceDetail.configuration.ports && (
                      <div className="mb-6">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">ポート設定</h3>
                        <div className="grid gap-2">
                          {serviceDetail.configuration.ports.map((port, index) => (
                            <div key={index} className="flex items-center gap-4 p-2 bg-gray-50 dark:bg-gray-700 rounded">
                              <span className="font-mono text-blue-600 dark:text-blue-400">:{port.port}</span>
                              <span className="text-sm text-gray-600 dark:text-gray-300">{port.protocol}</span>
                              <span className="text-sm text-gray-500 dark:text-gray-400">- {port.description}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {serviceDetail.configuration.environmentVariables && (
                      <div className="mb-6">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">環境変数</h3>
                        <div className="space-y-3">
                          {serviceDetail.configuration.environmentVariables.map((envVar, index) => (
                            <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
                              <code className="font-mono text-green-600 dark:text-green-400">{envVar.name}</code>
                              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{envVar.description}</p>
                              <code className="block mt-2 text-xs text-gray-500 dark:text-gray-400">
                                {envVar.example}
                              </code>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {serviceDetail.configuration.files && (
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">設定ファイル</h3>
                        <ul className="space-y-1">
                          {serviceDetail.configuration.files.map((file, index) => (
                            <li key={index} className="text-sm text-gray-600 dark:text-gray-300">
                              <code className="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                                {file}
                              </code>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Shortcuts Section */}
            {serviceDetail.shortcuts && serviceDetail.shortcuts.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="ショートカットキー" icon={Terminal} section="shortcuts" count={serviceDetail.shortcuts.length} />
                {expandedSections.shortcuts && (
                  <div className="p-6 pt-0">
                    <div className="grid md:grid-cols-2 gap-3">
                      {serviceDetail.shortcuts.map((shortcut, index) => (
                        <div key={index} className="flex items-center gap-3 p-2">
                          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-sm font-mono">
                            {shortcut.keys}
                          </kbd>
                          <span className="text-gray-700 dark:text-gray-300">{shortcut.action}</span>
                          {shortcut.context && (
                            <span className="text-xs text-gray-500 dark:text-gray-400">({shortcut.context})</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Integrations Section */}
            {serviceDetail.integrations && serviceDetail.integrations.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="連携サービス" icon={Users} section="integrations" count={serviceDetail.integrations.length} />
                {expandedSections.integrations && (
                  <div className="p-6 pt-0">
                    <div className="grid md:grid-cols-2 gap-4">
                      {serviceDetail.integrations.map((integration, index) => (
                        <div key={index} className="p-4 border dark:border-gray-700 rounded-lg">
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                            {integration.service}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                            {integration.description}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {integration.howTo}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* FAQ Section */}
            {serviceDetail.faq && serviceDetail.faq.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="よくある質問" icon={HelpCircle} section="faq" count={serviceDetail.faq.length} />
                {expandedSections.faq && (
                  <div className="p-6 pt-0">
                    <div className="space-y-4">
                      {serviceDetail.faq.map((item, index) => (
                        <div key={index} className="border-b dark:border-gray-700 pb-4 last:border-0">
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                            Q: {item.question}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300">
                            A: {item.answer}
                          </p>
                          {item.category && (
                            <span className="inline-block mt-2 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                              {item.category}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Troubleshooting Section */}
            {serviceDetail.troubleshooting && serviceDetail.troubleshooting.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6 overflow-hidden">
                <SectionHeader title="トラブルシューティング" icon={Wrench} section="troubleshooting" count={serviceDetail.troubleshooting.length} />
                {expandedSections.troubleshooting && (
                  <div className="p-6 pt-0">
                    <div className="space-y-4">
                      {serviceDetail.troubleshooting.map((item, index) => (
                        <div key={index} className="p-4 border dark:border-gray-700 rounded-lg">
                          <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                                {item.issue}
                              </h3>
                              <p className="text-gray-700 dark:text-gray-300 mb-2">
                                <strong>解決方法:</strong> {item.solution}
                              </p>
                              {item.relatedError && (
                                <code className="inline-block text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-2 py-1 rounded mb-2">
                                  {item.relatedError}
                                </code>
                              )}
                              {item.preventiveMeasure && (
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  <strong>予防策:</strong> {item.preventiveMeasure}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Resources Section */}
            {serviceDetail.resources && serviceDetail.resources.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                <SectionHeader title="参考資料" icon={BookOpen} section="resources" count={serviceDetail.resources.length} />
                {expandedSections.resources && (
                  <div className="p-6 pt-0">
                    <div className="grid md:grid-cols-2 gap-4">
                      {serviceDetail.resources.map((resource, index) => (
                        <a
                          key={index}
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-3 p-3 border dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded">
                                {resource.type}
                              </span>
                              {resource.language && (
                                <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded">
                                  {resource.language}
                                </span>
                              )}
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 font-medium">
                              {resource.title}
                            </p>
                          </div>
                          <ExternalLink className="w-4 h-4 text-gray-400" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          /* Fallback to simple display for services without detailed info */
          <>
            {/* Features Section */}
            {service.features && service.features.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 mb-8">
                <div className="flex items-center gap-2 mb-6">
                  <Sparkles className="w-6 h-6 text-yellow-500" />
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                    主な機能
                  </h2>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  {service.features.map((feature, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                    >
                      <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tags Section */}
            {service.tags && service.tags.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
                  タグ
                </h2>
                <div className="flex flex-wrap gap-2">
                  {service.tags.map(tag => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default ServicePage;