/**
 * Dynamic URL Resolution
 * Automatically detects the correct Tailscale hostname
 */

// Cache the hostname to avoid repeated lookups
let cachedHostname: string | null = null;

/**
 * Get the Tailscale hostname
 * Uses environment variable or defaults to known hostname
 */
export function getTailscaleHostname(): string {
  // Return cached value if available
  if (cachedHostname) {
    return cachedHostname;
  }

  // Use environment variable if available, otherwise use default
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://home-lab-01.tail4ed625.ts.net';
  cachedHostname = baseUrl.replace('https://', '').replace('http://', '');
  return cachedHostname;
}

/**
 * Build the base URL dynamically
 */
export function getBaseUrl(): string {
  if (typeof window !== 'undefined') {
    // Client-side: use current location if on same domain
    const currentHost = window.location.hostname;
    if (currentHost.includes('tail4ed625.ts.net')) {
      return `https://${currentHost}`;
    }
  }

  // Server-side or fallback: use Tailscale hostname
  return `https://${getTailscaleHostname()}`;
}

/**
 * Build service URL with dynamic base
 */
export function buildDynamicServiceUrl(port: number, path: string = '/'): string {
  // For localhost development, use direct HTTP access
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return `http://localhost:${port}${path}`;
  }

  // For production, use dynamic base URL
  return `${getBaseUrl()}:${port}${path}`;
}