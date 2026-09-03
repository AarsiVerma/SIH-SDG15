/** Language catalog client for frontend copy. */

interface LanguageCatalog {
  forbidden_terms: string[];
  messages: Record<string, { title: string; body: string; layer: string }>;
  disclaimers: {
    evidence: string;
    wildlife: string;
    ai_outputs: string;
  };
}

let catalogCache: LanguageCatalog | null = null;

export async function fetchLanguageCatalog(): Promise<LanguageCatalog> {
  if (catalogCache) return catalogCache;

  const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${base}/api/v1/language`);
  if (!response.ok) throw new Error("Failed to fetch language catalog");
  catalogCache = await response.json();
  return catalogCache;
}

export function getMessage(key: string): { title: string; body: string } | null {
  if (!catalogCache) return null;
  const msg = catalogCache.messages[key];
  return msg ? { title: msg.title, body: msg.body } : null;
}

export function getDisclaimer(key: string): string | null {
  if (!catalogCache) return null;
  return catalogCache.disclaimers[key] || null;
}

export function assertCopyAllowed(text: string): void {
  if (!catalogCache) return;
  const lowered = text.toLowerCase();
  for (const term of catalogCache.forbidden_terms) {
    if (lowered.includes(term)) {
      throw new Error(`Forbidden term in copy: ${term}`);
    }
  }
}

export function clearCache() {
  catalogCache = null;
}