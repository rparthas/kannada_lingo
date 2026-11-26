import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { LessonSummary, LevelSummary } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

type LessonWithUnit = LessonSummary;

interface UnitGroup {
  unitId: string;
  unitTitle: string;
  unitDescription?: string;
  lessons: LessonWithUnit[];
}

function findRecommendedLesson(lessons: LessonWithUnit[]): LessonWithUnit | null {
  return lessons.find((l) => !l.completed) ?? null;
}

function groupLessonsByUnit(lessons: LessonWithUnit[]): UnitGroup[] {
  const map = new Map<string, UnitGroup>();
  for (const lesson of lessons) {
    const existing = map.get(lesson.unitId);
    if (existing) {
      existing.lessons.push(lesson);
    } else {
      map.set(lesson.unitId, {
        unitId: lesson.unitId,
        unitTitle: lesson.unitTitle,
        unitDescription: undefined,
        lessons: [lesson],
      });
    }
  }
  return Array.from(map.values());
}

export function LearnScreen() {
  const [levels, setLevels] = useState<LevelSummary[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [lessons, setLessons] = useState<LessonWithUnit[]>([]);

  useEffect(() => {
    void tauriApi.listLevels().then((lv) => {
      setLevels(lv);
      if (lv[0]) setSelectedLevel(lv[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedLevel) return;
    void tauriApi.listLessonsForLevel(selectedLevel).then(setLessons);
  }, [selectedLevel]);

  const level = levels.find((l) => l.id === selectedLevel);
  const unitGroups = groupLessonsByUnit(lessons);
  const recommendedLesson = findRecommendedLesson(lessons);

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Learn</h1>
      <div className="mt-4 flex gap-2 overflow-x-auto">
        {levels.map((lv) => (
          <button
            key={lv.id}
            type="button"
            onClick={() => setSelectedLevel(lv.id)}
            className={`whitespace-nowrap rounded-full px-4 py-2 text-sm ${
              selectedLevel === lv.id ? "bg-amber-500 text-white" : "bg-stone-100"
            }`}
          >
            {lv.title}
          </button>
        ))}
      </div>
      {level ? (
        <p className="mt-3 text-sm text-stone-600">
          {level.completedLessons}/{level.totalLessons} lessons complete
        </p>
      ) : null}

      {recommendedLesson && (
        <div className="mt-4 rounded-xl bg-amber-50 p-4 ring-1 ring-amber-200">
          <p className="text-sm font-medium text-amber-900">Recommended next</p>
          <Link
            to={`/lesson/${recommendedLesson.id}`}
            className="mt-2 block rounded-lg bg-white p-3 shadow-sm ring-1 ring-stone-200"
          >
            <p className="font-semibold text-stone-900">{recommendedLesson.title}</p>
            <p className="text-sm text-stone-500">
              ~{recommendedLesson.estimatedMinutes} min
            </p>
          </Link>
        </div>
      )}

      <div className="mt-4 space-y-6">
        {unitGroups.map((group) => (
          <section key={group.unitId}>
            <h2 className="text-lg font-semibold text-stone-900">{group.unitTitle}</h2>
            <ul className="mt-2 space-y-3 md:grid md:grid-cols-2 md:gap-4 md:space-y-0">
              {group.lessons.map((lesson) => (
                <li key={lesson.id}>
                  <Link
                    to={`/lesson/${lesson.id}`}
                    className="block rounded-2xl bg-white p-4 shadow-sm ring-1 ring-stone-200"
                  >
                    <p className="font-semibold text-stone-900">{lesson.title}</p>
                    <p className="text-sm text-stone-500">
                      ~{lesson.estimatedMinutes} min {lesson.completed ? "· ✓ done" : ""}
                    </p>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}