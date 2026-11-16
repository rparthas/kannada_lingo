import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ExerciseRenderer,
  type ExerciseResult,
} from "../../components/exercises/ExerciseRenderer";
import { gradeFromAttempt, scheduleReview } from "../../domain/revision/sm2";
import { sumXpFromAttempts, xpForExercise } from "../../domain/progress/xp";
import type { LessonDetail } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

export function LessonPlayerScreen() {
  const { lessonId = "" } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [index, setIndex] = useState(0);
  const [lessonXp, setLessonXp] = useState(0);
  const [lessonCompleted, setLessonCompleted] = useState(false);

  useEffect(() => {
    if (!lessonId) return;
    void (async () => {
      const [detail, resume] = await Promise.all([
        tauriApi.getLessonDetail(lessonId),
        tauriApi.prepareLesson(lessonId),
      ]);
      const sessionXp = sumXpFromAttempts(
        resume.attempts.map((a) => ({
          exerciseType: a.exerciseType,
          isCorrect: a.isCorrect,
        })),
      );
      const allDone =
        !resume.lessonCompleted &&
        detail.exercises.length > 0 &&
        resume.resumeIndex >= detail.exercises.length;
      if (allDone) {
        await tauriApi.completeLesson(lessonId, sessionXp);
      }
      const completed = resume.lessonCompleted || allDone;
      setLesson(detail);
      setLessonCompleted(completed);
      setIndex(
        completed
          ? 0
          : Math.min(resume.resumeIndex, Math.max(0, detail.exercises.length - 1)),
      );
      setLessonXp(sessionXp);
    })();
  }, [lessonId]);

  const exercise = lesson?.exercises[index];

  const onComplete = useCallback(
    async (result: ExerciseResult) => {
      if (!exercise || !lesson) return;

      const prior = exercise.learningItemId
        ? await tauriApi.getItemScheduleState(exercise.learningItemId)
        : { easeFactor: 2.5, intervalDays: 0, repetitions: 0, masteryStatus: "new" };

      const grade = gradeFromAttempt({
        isCorrect: result.isCorrect,
        selfAssessedConfident: result.selfAssessed,
        wasDifficult: !result.isCorrect,
      });
      const schedule = scheduleReview(
        {
          easeFactor: prior.easeFactor,
          intervalDays: prior.intervalDays,
          repetitions: prior.repetitions,
        },
        grade,
      );
      const xp = xpForExercise(exercise.exerciseType, result.isCorrect);
      const nextLessonXp = lessonXp + xp;
      setLessonXp(nextLessonXp);

      if (!lessonCompleted) {
        await tauriApi.recordExerciseAttempt({
          exerciseId: exercise.id,
          learningItemId: exercise.learningItemId,
          isCorrect: result.isCorrect,
          responseJson: result.response,
          selfAssessed: result.selfAssessed,
          xpAmount: xp,
          lessonId: lesson.id,
          easeFactor: schedule.easeFactor,
          intervalDays: schedule.nextIntervalDays,
          repetitions: schedule.repetitions,
          masteryStatus: schedule.masteryStatus,
        });
      }

      if (index + 1 >= lesson.exercises.length) {
        if (!lessonCompleted) {
          await tauriApi.completeLesson(lesson.id, nextLessonXp);
        }
        navigate("/learn", { replace: true });
      } else {
        setIndex((i) => i + 1);
      }
    },
    [exercise, index, lesson, lessonCompleted, lessonXp, navigate],
  );

  if (!lesson) {
    return <p className="p-6 text-stone-600">Loading lesson…</p>;
  }

  const progressPct = lesson.exercises.length
    ? Math.round(((index + 1) / lesson.exercises.length) * 100)
    : 0;

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <button
        type="button"
        className="text-sm text-amber-800"
        onClick={() => navigate(-1)}
      >
        ← Back
      </button>
      <h1 className="mt-2 text-2xl font-bold text-stone-900">{lesson.title}</h1>
      {lessonCompleted ? (
        <p className="mt-1 text-sm text-emerald-700">Review mode — progress already saved</p>
      ) : (
        <p className="mt-1 text-sm text-stone-500">
          Exercise {index + 1} of {lesson.exercises.length} · {lessonXp} XP this session
        </p>
      )}
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-200">
        <div className="h-full bg-amber-500 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="mt-6">
        {exercise ? (
          <ExerciseRenderer
            key={exercise.id}
            exercise={exercise}
            onComplete={(r) => void onComplete(r)}
          />
        ) : null}
      </div>
    </div>
  );
}