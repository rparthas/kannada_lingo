import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

type Phrase = {
  id: string;
  kannada_text: string;
  transliteration: string;
  english_meaning: string;
};

type CurriculumData = {
  learning_items: Array<{
    id: string;
    kannada_text: string;
    transliteration: string;
    english_meaning: string;
  }>;
};

export function PhraseSearchScreen() {
  const [phrases, setPhrases] = useState<Phrase[]>([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    import("../../../content/curriculum/beginner-path.json")
      .then((module) => {
        const data = module.default as CurriculumData;
        const allPhrases = data.learning_items.map((item) => ({
          id: item.id,
          kannada_text: item.kannada_text,
          transliteration: item.transliteration,
          english_meaning: item.english_meaning,
        }));
        setPhrases(allPhrases);
      })
      .catch((error) => {
        console.error("Failed to load phrase data", error);
      });
  }, []);

  const filteredPhrases = phrases.filter((phrase) => {
    const term = searchTerm.toLowerCase();
    return (
      phrase.kannada_text.toLowerCase().includes(term) ||
      phrase.transliteration.toLowerCase().includes(term) ||
      phrase.english_meaning.toLowerCase().includes(term)
    );
  });

  return (
    <div className="mx-auto max-w-3xl space-y-4 px-4 py-6">
      <h1 className="text-2xl font-bold text-stone-900">Phrase Search</h1>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Search by English, transliteration, or Kannada..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 rounded border border-stone-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-500"
        />
      </div>

      {filteredPhrases.length === 0 ? (
        <p className="text-stone-600">No phrases match your search.</p>
      ) : (
        <ul className="space-y-3">
          {filteredPhrases.map((phrase) => (
            <li key={phrase.id} className="rounded border border-stone-200 bg-white p-3 shadow-sm">
              <Link
                to={`/phrase/${phrase.id}`}
                className="text-lg font-medium text-amber-600 hover:underline"
              >
                {phrase.kannada_text} ({phrase.transliteration})
              </Link>
              <p className="text-sm text-stone-600">{phrase.english_meaning}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}