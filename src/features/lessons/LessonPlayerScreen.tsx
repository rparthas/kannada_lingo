import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ExerciseRenderer,
  type ExerciseResult,
} from "../../components/exercises/ExerciseRenderer";
import { gradeFromAttempt, scheduleReview } from "../../domain/revision/sm2";
import type { LessonDetail } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

export function LessonPlayerScreen() {
  const { lessonId = "" } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [index, setIndex] = useState(0);
  const [lessonXp, setLessonXp] = useState(0);

  useEffect(() => {
    if (!lessonId) return;
    void tauriApi.getLessonDetail(lessonId).then(setLesson);
  }, [lessonId]);

  const exercise = lesson?.exercises[index];

  const onComplete = useCallback(
    async (result: ExerciseResult) => {
      if (!exercise || !lesson) return;
      const grade = gradeFromAttempt({
        isCorrect: result.isCorrect,
        selfAssessedConfident: result.selfAssessed,
        wasDifficult: !result.isCorrect,
      });
      const schedule = scheduleReview(
        { easeFactor: 2.5, intervalDays: 0, repetitions: 0 },
        grade,
      );
      const xp = result.isCorrect ? 10 : 4;
      setLessonXp((v) => v + xp);
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
        masteryStatus: schedule.masteryStatus,
      });
      if (index + 1 >= lesson.exercises.length) {
        await tauriApi.completeLesson(lesson.id, lessonXp + xp);
        navigate("/learn", { replace: true });
      } else {
        setIndex((i) => i + 1);
      }
    },
    [exercise, index, lesson, lessonXp, navigate],
  );

  if (!lesson) {
    return <p className="p-6 text-stone-600">Loading lesson…</p>;
  }

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
      <p className="mt-1 text-sm text-stone-500">
        Exercise {index + 1} of {lesson.exercises.length}
      </p>
      <div className="mt-6">
        {exercise ? (
          <ExerciseRenderer key={exercise.id} exercise={exercise} onComplete={(r) => void onComplete(r)} />
        ) : null}
      </div>
    </div>
  );
}