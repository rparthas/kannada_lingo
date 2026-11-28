export interface SearchablePhrase {
  kannada_text: string;
  transliteration: string;
  english_meaning: string;
}

/**
 * Offline phrase filter used by Phrase Search. Runs entirely against the
 * bundled curriculum, so it works in airplane mode after first launch.
 */
export function filterPhrases<T extends SearchablePhrase>(
  phrases: T[],
  searchTerm: string,
): T[] {
  const term = searchTerm.trim().toLowerCase();
  if (!term) return phrases;
  return phrases.filter(
    (phrase) =>
      phrase.kannada_text.toLowerCase().includes(term) ||
      phrase.transliteration.toLowerCase().includes(term) ||
      phrase.english_meaning.toLowerCase().includes(term),
  );
}
