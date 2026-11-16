import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import type { HomeSummary } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

export function HomeScreen() {
  const [summary, setSummary] = useState<HomeSummary | null>(null);

  useEffect(() => {
    void tauriApi.getHomeSummary().then(setSummary);
  }, []);

  const goalPct = summary
    ? Math.min(100, Math.round((summary.todayXp / summary.dailyGoalXp) * 100))
    : 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 pb-28 pt-4">
      <header>
        <h1 className="text-2xl font-bold text-stone-900">Today</h1>
        <p className="text-stone-600">A focused session beats a long study block.</p>
      </header>

      <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-stone-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-stone-500">Daily goal</p>
            <p className="text-xl font-semibold">
              {summary?.todayXp ?? 0} / {summary?.dailyGoalXp ?? 50} XP
            </p>
          </div>
          <p className="text-3xl font-bold text-amber-600">{goalPct}%</p>
        </div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-stone-100">
          <div className="h-full bg-amber-500" style={{ width: `${goalPct}%` }} />
        </div>
        <p className="mt-3 text-sm text-stone-600">
          Streak (goal days, last 30d): {summary?.streakDays ?? 0}
        </p>
      </section>

      {summary?.continueLessonId ? (
        <Link
          to={`/lesson/${summary.continueLessonId}`}
          className="block rounded-2xl bg-amber-500 p-5 font-semibold text-white shadow-sm"
        >
          Continue: {summary.continueLessonTitle}
        </Link>
      ) : null}

      <section className="rounded-2xl bg-stone-900 p-5 text-white">
        <p className="text-sm text-stone-300">Due revision</p>
        <p className="text-3xl font-bold">{summary?.dueReviews ?? 0}</p>
        <Link to="/practice" className="mt-3 inline-block text-amber-300 underline">
          Open practice
        </Link>
      </section>
    </div>
  );
}