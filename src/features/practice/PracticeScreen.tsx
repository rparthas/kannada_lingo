import { useEffect, useState } from "react";
import { tauriApi } from "../../services/api/tauri";

interface ReviewItem {
  learningItemId: string;
  kannadaText: string;
  transliteration: string;
  englishMeaning: string;
}

export function PracticeScreen() {
  const [queue, setQueue] = useState<ReviewItem[]>([]);

  useEffect(() => {
    void tauriApi.getReviewQueue().then((items) => setQueue(items as ReviewItem[]));
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Practice</h1>
      <p className="mt-1 text-stone-600">Spaced repetition queue (overdue items first).</p>
      {queue.length === 0 ? (
        <p className="mt-8 rounded-2xl bg-white p-6 text-stone-600 ring-1 ring-stone-200">
          Nothing due right now. Complete a lesson to start scheduling reviews.
        </p>
      ) : (
        <ul className="mt-6 space-y-3">
          {queue.map((item) => (
            <li key={item.learningItemId} className="rounded-2xl bg-white p-4 ring-1 ring-stone-200">
              <p className="text-2xl font-semibold kannada">{item.kannadaText}</p>
              <p className="text-amber-800">{item.transliteration}</p>
              <p className="mt-1 text-stone-700">{item.englishMeaning}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}