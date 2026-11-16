import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { LearningItemDetail } from "../../services/api/tauri";
import { PhraseAudioControls } from "../../components/audio/PhraseAudioControls";
import { tauriApi } from "../../services/api/tauri";

export function PhraseDetailScreen() {
  const { itemId = "" } = useParams();
  const [detail, setDetail] = useState<LearningItemDetail | null>(null);

  useEffect(() => {
    if (!itemId) return;
    void tauriApi.getLearningItemDetail(itemId).then(setDetail);
  }, [itemId]);

  if (!detail) {
    return <p className="p-6 text-stone-600">Loading phrase…</p>;
  }

  const mastery = detail.progress?.masteryStatus ?? "new";

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <Link to="/progress" className="text-sm text-amber-800">
        ← Progress
      </Link>
      <div className="mt-4 rounded-2xl bg-white p-5 ring-1 ring-stone-200">
        <p className="text-4xl font-semibold kannada">{detail.kannadaText}</p>
        <p className="mt-2 text-xl text-amber-800">{detail.transliteration}</p>
        <p className="mt-3 text-lg text-stone-900">{detail.englishMeaning}</p>
        {detail.literalTranslation ? (
          <p className="mt-2 text-sm text-stone-500">
            Literal: {detail.literalTranslation}
          </p>
        ) : null}
        {detail.contextNote ? (
          <p className="mt-3 text-sm text-stone-600">{detail.contextNote}</p>
        ) : null}
        <PhraseAudioControls learningItemId={detail.id} className="mt-4" />
      </div>

      <section className="mt-6 grid gap-3 md:grid-cols-3">
        <Stat label="Mastery" value={mastery} />
        <Stat label="Attempts" value={detail.attemptCount} />
        <Stat
          label="Accuracy"
          value={
            detail.attemptCount > 0
              ? `${Math.round((detail.correctCount / detail.attemptCount) * 100)}%`
              : "—"
          }
        />
      </section>

      {detail.recentAttempts.length > 0 ? (
        <section className="mt-6">
          <h2 className="font-semibold text-stone-900">Recent attempts</h2>
          <ul className="mt-3 space-y-2">
            {detail.recentAttempts.map((row, i) => (
              <li
                key={`${row.attemptedAt}-${i}`}
                className="flex items-center justify-between rounded-xl bg-white px-4 py-3 text-sm ring-1 ring-stone-200"
              >
                <span className="text-stone-700">{row.exerciseType.replace(/_/g, " ")}</span>
                <span className={row.isCorrect ? "text-emerald-700" : "text-amber-800"}>
                  {row.isCorrect ? "Correct" : "Needs work"}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : (
        <p className="mt-6 text-sm text-stone-500">
          Complete a lesson or practice item to build history for this phrase.
        </p>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl bg-white p-4 ring-1 ring-stone-200">
      <p className="text-sm text-stone-500">{label}</p>
      <p className="text-xl font-semibold capitalize text-stone-900">{value}</p>
    </div>
  );
}