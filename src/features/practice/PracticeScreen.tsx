import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { evaluateKannadaRecall } from "../../domain/exercises/evaluate";
import { gradeFromAttempt, scheduleReview } from "../../domain/revision/sm2";
import { xpForExercise } from "../../domain/progress/xp";
import type { ReviewQueueItem } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

export function PracticeScreen() {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [active, setActive] = useState<ReviewQueueItem | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadQueue = useCallback(() => {
    void tauriApi.getReviewQueue().then((items) => {
      setQueue(items);
      setActive(items[0] ?? null);
      setAnswer("");
      setFeedback(null);
    });
  }, []);

  useEffect(() => {
    loadQueue();
  }, [loadQueue]);

  async function checkAnswer() {
    if (!active?.exerciseId) return;
    const prior = await tauriApi.getItemScheduleState(active.learningItemId);
    const isCorrect = evaluateKannadaRecall(answer, {
      kannadaText: active.kannadaText,
      transliteration: active.transliteration,
      englishMeaning: active.englishMeaning,
      acceptedAnswers: active.acceptedAnswers,
    });
    setFeedback(
      isCorrect
        ? "Nice recall — scheduled for later review."
        : `Try “${active.transliteration}” or the Kannada script.`,
    );
    const schedule = scheduleReview(
      {
        easeFactor: prior.easeFactor,
        intervalDays: prior.intervalDays,
        repetitions: prior.repetitions,
      },
      gradeFromAttempt({ isCorrect, wasDifficult: !isCorrect }),
    );
    const xp = xpForExercise(active.exerciseType ?? "english_to_kannada", isCorrect);
    await tauriApi.recordExerciseAttempt({
      exerciseId: active.exerciseId,
      learningItemId: active.learningItemId,
      isCorrect,
      responseJson: { answer, mode: "review" },
      xpAmount: xp,
      easeFactor: schedule.easeFactor,
      intervalDays: schedule.nextIntervalDays,
      repetitions: schedule.repetitions,
      masteryStatus: schedule.masteryStatus,
    });
  }

  function nextItem() {
    if (!active) return;
    const rest = queue.filter((i) => i.learningItemId !== active.learningItemId);
    setQueue(rest);
    setActive(rest[0] ?? null);
    setFeedback(null);
    setAnswer("");
    if (rest.length === 0) loadQueue();
  }

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Practice</h1>
      <p className="mt-1 text-stone-600">Spaced repetition queue (overdue items first).</p>

      {active ? (
        <section className="mt-6 space-y-4 rounded-2xl bg-white p-5 ring-1 ring-stone-200">
          <p className="text-sm text-stone-500">Recall challenge</p>
          <p className="text-lg font-medium text-stone-900">{active.englishMeaning}</p>
          <input
            className="w-full rounded-xl border border-stone-300 px-4 py-3 text-lg"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type Kannada or transliteration"
            autoCapitalize="off"
            autoCorrect="off"
          />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="flex-1 rounded-xl bg-amber-500 py-3 font-semibold text-white disabled:opacity-50"
              disabled={!answer.trim() || !!feedback}
              onClick={() => void checkAnswer()}
            >
              Check
            </button>
            <Link
              to={`/phrase/${active.learningItemId}`}
              className="rounded-xl border border-stone-200 px-4 py-3 text-sm text-amber-800"
            >
              Phrase details
            </Link>
          </div>
          {feedback ? (
            <div className="space-y-2">
              <p className="text-sm text-stone-700">{feedback}</p>
              <p className="text-2xl font-semibold kannada">{active.kannadaText}</p>
              <button
                type="button"
                className="w-full rounded-xl bg-stone-900 py-3 font-semibold text-white"
                onClick={nextItem}
              >
                Next in queue
              </button>
            </div>
          ) : null}
        </section>
      ) : (
        <p className="mt-8 rounded-2xl bg-white p-6 text-stone-600 ring-1 ring-stone-200">
          Nothing due right now. Complete a lesson to start scheduling reviews.
        </p>
      )}

      {queue.length > 1 ? (
        <ul className="mt-6 space-y-2">
          <p className="text-sm font-medium text-stone-500">Also due</p>
          {queue.slice(1, 6).map((item) => (
            <li
              key={item.learningItemId}
              className="flex items-center justify-between rounded-xl bg-white px-4 py-3 text-sm ring-1 ring-stone-200"
            >
              <span className="kannada">{item.kannadaText}</span>
              <button
                type="button"
                className="text-amber-800"
                onClick={() => {
                  setActive(item);
                  setAnswer("");
                  setFeedback(null);
                }}
              >
                Practice
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}