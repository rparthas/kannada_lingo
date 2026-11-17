import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { LearningItemDetail } from "../../services/api/tauri";
import { PhraseAudioControls } from "../../components/audio/PhraseAudioControls";
import { getAIContentProvider } from "../../services/ai";
import type { GrammarExplanation } from "../../services/ai";
import { tauriApi } from "../../services/api/tauri";

function grammarPatternForItem(itemId: string): string {
  if (itemId.includes("sari")) return "pattern-sari";
  return "default";
}

export function PhraseDetailScreen() {
  const { itemId = "" } = useParams();
  const [detail, setDetail] = useState<LearningItemDetail | null>(null);
  const [grammar, setGrammar] = useState<GrammarExplanation | null>(null);
  const [grammarLoading, setGrammarLoading] = useState(false);
  const [grammarError, setGrammarError] = useState<string | null>(null);

  useEffect(() => {
    if (!itemId) return;
    void tauriApi.getLearningItemDetail(itemId).then(setDetail);
  }, [itemId]);

  async function loadGrammarExplanation() {
    if (!itemId) return;
    setGrammarLoading(true);
    setGrammarError(null);
    try {
      const provider = getAIContentProvider();
      const explanation = await provider.explainGrammar({
        patternId: grammarPatternForItem(itemId),
        exampleItemIds: [itemId],
      });
      setGrammar(explanation);
    } catch (err) {
      setGrammarError(err instanceof Error ? err.message : "Could not load explanation.");
    } finally {
      setGrammarLoading(false);
    }
  }

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

      {detail.progress || detail.nextReviewAt ? (
        <section className="mt-6 rounded-2xl bg-white p-5 ring-1 ring-stone-200">
          <h2 className="font-semibold text-stone-900">Review schedule</h2>
          <dl className="mt-3 grid gap-2 text-sm md:grid-cols-3">
            {detail.progress ? (
              <>
                <ScheduleRow label="Interval" value={`${detail.progress.intervalDays} days`} />
                <ScheduleRow label="Ease" value={detail.progress.easeFactor.toFixed(2)} />
              </>
            ) : null}
            <ScheduleRow
              label="Next review"
              value={
                detail.nextReviewAt
                  ? new Date(detail.nextReviewAt).toLocaleString()
                  : "Not scheduled"
              }
            />
          </dl>
        </section>
      ) : null}

      <section className="mt-6 rounded-2xl bg-amber-50 p-5 ring-1 ring-amber-200">
        <h2 className="font-semibold text-stone-900">Grammar insight (AI)</h2>
        <p className="mt-1 text-sm text-stone-600">
          Supplementary notes — mock provider in dev; no data leaves your device in this build.
        </p>
        {grammar ? (
          <div className="mt-3 text-sm text-stone-800">
            <p className="font-medium">{grammar.title}</p>
            <p className="mt-2">{grammar.explanationEn}</p>
          </div>
        ) : (
          <button
            type="button"
            className="mt-3 rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            disabled={grammarLoading}
            onClick={() => void loadGrammarExplanation()}
          >
            {grammarLoading ? "Loading…" : "Explain this phrase"}
          </button>
        )}
        {grammarError ? <p className="mt-2 text-sm text-red-700">{grammarError}</p> : null}
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

function ScheduleRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-stone-500">{label}</dt>
      <dd className="font-medium text-stone-900">{value}</dd>
    </div>
  );
}