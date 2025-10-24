import { encodingForModel } from 'js-tiktoken';

// Claude 3.5 Sonnetで使用されるエンコーディング（cl100k_base）
const encoding = encodingForModel('gpt-4');

/**
 * プロンプトのトークン数を計算
 */
export function countTokens(text: string): number {
  if (!text) return 0;
  const tokens = encoding.encode(text);
  return tokens.length;
}

/**
 * プロンプトの構造分析結果
 */
export interface PromptAnalysis {
  tokenCount: number;
  hasXmlStructure: boolean;
  hasExamples: boolean;
  hasInstructions: boolean;
  isConcise: boolean; // <5K tokens
  structureScore: number; // 0-100
  xmlTags: string[];
  recommendations: string[];
}

/**
 * プロンプトを分析してAnthropicベストプラクティスに準拠しているか確認
 */
export function analyzePrompt(systemPrompt: string): PromptAnalysis {
  const tokenCount = countTokens(systemPrompt);

  // XML構造の検出
  const xmlTagRegex = /<(\w+)>/g;
  const xmlTags = Array.from(new Set(
    Array.from(systemPrompt.matchAll(xmlTagRegex), m => m[1])
  ));

  const hasXmlStructure = xmlTags.length > 0;
  const hasExamples = /<example/.test(systemPrompt);
  const hasInstructions = /<instructions/.test(systemPrompt);
  const isConcise = tokenCount < 5000;

  // 構造スコアの計算（0-100）
  let structureScore = 0;
  if (hasXmlStructure) structureScore += 30;
  if (hasExamples) structureScore += 25;
  if (hasInstructions) structureScore += 25;
  if (isConcise) structureScore += 20;

  // 改善推奨事項
  const recommendations: string[] = [];

  if (!hasXmlStructure) {
    recommendations.push('XMLタグで構造化してください（<instructions>, <example>等）');
  }
  if (!hasExamples) {
    recommendations.push('<example>タグで具体例を追加してください');
  }
  if (!hasInstructions) {
    recommendations.push('<instructions>タグで明確なルールを定義してください');
  }
  if (tokenCount > 10000) {
    recommendations.push('トークン数が多すぎます（10K+）。簡潔化を推奨');
  } else if (tokenCount > 5000) {
    recommendations.push('トークン数が5K以上です。簡潔化を検討してください');
  }

  return {
    tokenCount,
    hasXmlStructure,
    hasExamples,
    hasInstructions,
    isConcise,
    structureScore,
    xmlTags,
    recommendations,
  };
}

/**
 * キャッシング推奨を取得（Claude 3.5 Sonnet基準）
 */
export function getCachingRecommendations(tokenCount: number): {
  shouldCache: boolean;
  estimatedSavings: string;
  threshold: number;
} {
  const CACHE_THRESHOLD = 1024; // Claude 3.5 Sonnetのキャッシング閾値
  const shouldCache = tokenCount >= CACHE_THRESHOLD;

  // キャッシングによる推定コスト削減（90%削減）
  const estimatedSavings = shouldCache
    ? '約90%のコスト削減が可能'
    : `あと${CACHE_THRESHOLD - tokenCount}トークンでキャッシング有効`;

  return {
    shouldCache,
    estimatedSavings,
    threshold: CACHE_THRESHOLD,
  };
}

/**
 * トークン数に応じた色を取得
 */
export function getTokenColor(tokenCount: number): string {
  if (tokenCount < 2000) return 'text-green-600';
  if (tokenCount < 5000) return 'text-yellow-600';
  if (tokenCount < 10000) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * トークン数に応じた背景色を取得
 */
export function getTokenBgColor(tokenCount: number): string {
  if (tokenCount < 2000) return 'bg-green-100 text-green-800';
  if (tokenCount < 5000) return 'bg-yellow-100 text-yellow-800';
  if (tokenCount < 10000) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
}
