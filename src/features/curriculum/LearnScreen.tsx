import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { LessonSummary, LevelSummary } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

export function LearnScreen() {
  const [levels, setLevels] = useState<LevelSummary[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [lessons, setLessons] = useState<LessonSummary[]>([]);

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
      <ul className="mt-4 space-y-3 md:grid md:grid-cols-2 md:gap-4 md:space-y-0">
        {lessons.map((lesson) => (
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
    </div>
  );
}