import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { save } from "@tauri-apps/plugin-dialog";
import { tauriApi } from "../../services/api/tauri";

export function ProgressScreen() {
  const [stats, setStats] = useState<Record<string, number>>({});

  useEffect(() => {
    void tauriApi.getProgressStats().then(setStats);
  }, []);

  async function exportBackup() {
    const file = await save({
      filters: [{ name: "Kannada Quest Backup", extensions: ["kqbackup.zip"] }],
      defaultPath: `kannada-quest-${new Date().toISOString().slice(0, 10)}.kqbackup.zip`,
    });
    if (!file) return;
    await tauriApi.exportLearningBackup(file);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Progress</h1>
      <div className="grid gap-3 md:grid-cols-2">
        <StatCard label="Mastered phrases" value={stats.masteredCount ?? 0} />
        <StatCard label="Learning / reviewing" value={stats.learningCount ?? 0} />
        <StatCard
          label="Recall accuracy"
          value={`${Math.round(stats.recallAccuracyPercent ?? 0)}%`}
        />
        <StatCard label="Total attempts" value={stats.totalAttempts ?? 0} />
      </div>
      <section className="rounded-2xl bg-white p-5 ring-1 ring-stone-200">
        <h2 className="font-semibold text-stone-900">Backup</h2>
        <p className="mt-1 text-sm text-stone-600">
          Export a portable ZIP to Files or iCloud Drive. Restore is available from Settings.
        </p>
        <button
          type="button"
          className="mt-4 rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white"
          onClick={() => void exportBackup()}
        >
          Export backup
        </button>
        <Link to="/settings" className="ml-3 text-sm text-amber-800 underline">
          Settings
        </Link>
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl bg-white p-4 ring-1 ring-stone-200">
      <p className="text-sm text-stone-500">{label}</p>
      <p className="text-2xl font-bold text-stone-900">{value}</p>
    </div>
  );
}