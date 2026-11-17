import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ExerciseRenderer, type ExerciseResult } from "../../components/exercises/ExerciseRenderer";
import { evaluateKannadaRecall } from "../../domain/exercises/evaluate";
import { gradeFromAttempt, scheduleReview, type ReviewGrade } from "../../domain/revision/sm2";
import { xpForExercise } from "../../domain/progress/xp";
import type { ExerciseDto, ReviewQueueItem } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

function queueItemToExercise(item: ReviewQueueItem): ExerciseDto | null {
  if (!item.exerciseId) return null;
  return {
    id: item.exerciseId,
    exerciseType: item.exerciseType ?? "english_to_kannada",
    learningItemId: item.learningItemId,
    prompt: item.exercisePrompt ?? {},
    learningItem: {
      id: item.learningItemId,
      kannadaText: item.kannadaText,
      transliteration: item.transliteration,
      englishMeaning: item.englishMeaning,
      acceptedAnswers: item.acceptedAnswers,
    },
  };
}

export function PracticeScreen() {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [active, setActive] = useState<ReviewQueueItem | null>(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [pendingGrade, setPendingGrade] = useState<{
    isCorrect: boolean;
    response: Record<string, unknown>;
    selfAssessed?: boolean;
  } | null>(null);

  const loadQueue = useCallback(() => {
    void tauriApi.getReviewQueue().then((items) => {
      setQueue(items);
      setActive(items[0] ?? null);
      setAnswer("");
      setFeedback(null);
      setPendingGrade(null);
    });
  }, []);

  useEffect(() => {
    loadQueue();
  }, [loadQueue]);

  const activeExercise = useMemo(
    () => (active ? queueItemToExercise(active) : null),
    [active],
  );

  async function persistReview(
    grade: ReviewGrade,
    meta: {
      isCorrect: boolean;
      response: Record<string, unknown>;
      selfAssessed?: boolean;
    },
  ) {
    if (!active?.exerciseId) return;
    const prior = await tauriApi.getItemScheduleState(active.learningItemId);
    const schedule = scheduleReview(
      {
        easeFactor: prior.easeFactor,
        intervalDays: prior.intervalDays,
        repetitions: prior.repetitions,
      },
      grade,
    );
    const xp = xpForExercise(active.exerciseType ?? "english_to_kannada", meta.isCorrect);
    await tauriApi.recordExerciseAttempt({
      exerciseId: active.exerciseId,
      learningItemId: active.learningItemId,
      isCorrect: meta.isCorrect,
      responseJson: { ...meta.response, mode: "review", grade },
      selfAssessed: meta.selfAssessed,
      xpAmount: xp,
      easeFactor: schedule.easeFactor,
      intervalDays: schedule.nextIntervalDays,
      repetitions: schedule.repetitions,
      masteryStatus: schedule.masteryStatus,
    });
    setFeedback(
      meta.isCorrect
        ? `Scheduled — next in ~${schedule.nextIntervalDays} day(s).`
        : "We'll show this again soon.",
    );
    setPendingGrade(null);
  }

  async function checkRecallAnswer() {
    if (!active?.exerciseId) return;
    const isCorrect = evaluateKannadaRecall(answer, {
      kannadaText: active.kannadaText,
      transliteration: active.transliteration,
      englishMeaning: active.englishMeaning,
      acceptedAnswers: active.acceptedAnswers,
    });
    setPendingGrade({
      isCorrect,
      response: { answer },
    });
    if (!isCorrect) {
      const grade = gradeFromAttempt({ isCorrect, wasDifficult: true });
      await persistReview(grade, { isCorrect, response: { answer } });
    } else {
      setFeedback("Pick how hard that felt:");
    }
  }

  async function onExerciseComplete(result: ExerciseResult) {
    setPendingGrade(result);
    if (!result.isCorrect) {
      const grade = gradeFromAttempt({
        isCorrect: result.isCorrect,
        wasDifficult: true,
        selfAssessedConfident: result.selfAssessed,
      });
      await persistReview(grade, result);
    } else if (result.selfAssessed === undefined) {
      setFeedback("Pick how hard that felt:");
    } else {
      const grade = gradeFromAttempt({
        isCorrect: true,
        selfAssessedConfident: result.selfAssessed,
      });
      await persistReview(grade, result);
    }
  }

  function nextItem() {
    if (!active) return;
    const rest = queue.filter((i) => i.learningItemId !== active.learningItemId);
    setQueue(rest);
    setActive(rest[0] ?? null);
    setFeedback(null);
    setAnswer("");
    setPendingGrade(null);
    if (rest.length === 0) loadQueue();
  }

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Practice</h1>
      <p className="mt-1 text-stone-600">
        Daily review session — {queue.length} item{queue.length === 1 ? "" : "s"} due.
      </p>

      {active ? (
        <section className="mt-6 space-y-4 rounded-2xl bg-white p-5 ring-1 ring-stone-200">
          <p className="text-sm text-stone-500">
            Due {new Date(active.nextReviewAt).toLocaleString()} ·{" "}
            {(active.exerciseType ?? "recall").replace(/_/g, " ")}
          </p>

          {activeExercise ? (
            <ExerciseRenderer exercise={activeExercise} onComplete={(r) => void onExerciseComplete(r)} />
          ) : (
            <>
              <p className="text-lg font-medium text-stone-900">{active.englishMeaning}</p>
              <input
                className="w-full rounded-xl border border-stone-300 px-4 py-3 text-lg"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type Kannada or transliteration"
                autoCapitalize="off"
                autoCorrect="off"
              />
              <button
                type="button"
                className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white disabled:opacity-50"
                disabled={!answer.trim() || !!feedback}
                onClick={() => void checkRecallAnswer()}
              >
                Check
              </button>
            </>
          )}

          {pendingGrade?.isCorrect && feedback?.startsWith("Pick") ? (
            <GradeBar onGrade={(g) => void persistReview(g, pendingGrade)} />
          ) : null}

          {feedback && !feedback.startsWith("Pick") ? (
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

          <Link
            to={`/phrase/${active.learningItemId}`}
            className="inline-block text-sm text-amber-800 underline"
          >
            Phrase details
          </Link>
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
                  setPendingGrade(null);
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

function GradeBar({ onGrade }: { onGrade: (grade: ReviewGrade) => void }) {
  const grades: { label: string; grade: ReviewGrade }[] = [
    { label: "Again", grade: 1 },
    { label: "Hard", grade: 3 },
    { label: "Good", grade: 4 },
    { label: "Easy", grade: 5 },
  ];
  return (
    <div className="flex flex-wrap gap-2">
      {grades.map((g) => (
        <button
          key={g.grade}
          type="button"
          className="flex-1 rounded-xl border border-stone-300 py-2 text-sm font-medium"
          onClick={() => onGrade(g.grade)}
        >
          {g.label}
        </button>
      ))}
    </div>
  );
}