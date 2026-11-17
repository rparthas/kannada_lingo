import { useEffect, useState } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import type { BackupManifest } from "../../services/api/tauri";
import { tauriApi } from "../../services/api/tauri";

export function SettingsScreen() {
  const [dailyGoal, setDailyGoal] = useState(50);
  const [goalSaved, setGoalSaved] = useState<string | null>(null);
  const [restoreError, setRestoreError] = useState<string | null>(null);
  const [pendingRestore, setPendingRestore] = useState<{
    path: string;
    manifest: BackupManifest;
  } | null>(null);

  useEffect(() => {
    void tauriApi.getLearnerProfile().then((p) => setDailyGoal(p.dailyGoalXp));
  }, []);

  async function saveDailyGoal() {
    setGoalSaved(null);
    try {
      await tauriApi.updateLearnerProfile(dailyGoal);
      setGoalSaved("Daily goal saved.");
    } catch (err) {
      setGoalSaved(err instanceof Error ? err.message : "Could not save goal.");
    }
  }

  async function importBackup() {
    setRestoreError(null);
    const file = await open({
      multiple: false,
      filters: [{ name: "Kannada Quest Backup", extensions: ["zip", "kqbackup.zip"] }],
    });
    if (!file || typeof file !== "string") return;
    try {
      const manifest = await tauriApi.validateLearningBackup(file);
      setPendingRestore({ path: file, manifest });
    } catch (err) {
      setRestoreError(err instanceof Error ? err.message : "Backup validation failed.");
    }
  }

  async function confirmRestore() {
    if (!pendingRestore) return;
    setRestoreError(null);
    try {
      await tauriApi.restoreLearningBackup(pendingRestore.path);
      window.location.reload();
    } catch (err) {
      setRestoreError(err instanceof Error ? err.message : "Restore failed.");
      setPendingRestore(null);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Settings</h1>

      <section className="mt-6 rounded-2xl bg-white p-5 ring-1 ring-stone-200">
        <h2 className="font-semibold">Daily XP goal</h2>
        <p className="mt-1 text-sm text-stone-600">Used for streaks and the Today progress bar.</p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <input
            type="number"
            min={10}
            max={500}
            className="w-28 rounded-xl border border-stone-300 px-3 py-2"
            value={dailyGoal}
            onChange={(e) => {
              const v = Number(e.target.value);
              if (!Number.isNaN(v)) setDailyGoal(Math.min(500, Math.max(10, v)));
            }}
          />
          <button
            type="button"
            className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white"
            onClick={() => void saveDailyGoal()}
          >
            Save
          </button>
        </div>
        {goalSaved ? <p className="mt-2 text-sm text-stone-600">{goalSaved}</p> : null}
      </section>

      <section className="mt-6 rounded-2xl bg-white p-5 ring-1 ring-stone-200">
        <h2 className="font-semibold">Restore backup</h2>
        <p className="mt-1 text-sm text-stone-600">
          Validates manifest and checksum before replacing the live database. A safety copy is kept
          alongside the database file.
        </p>
        <button
          type="button"
          className="mt-4 rounded-xl border border-stone-300 px-4 py-2 text-sm"
          onClick={() => void importBackup()}
        >
          Import backup…
        </button>
        {restoreError ? <p className="mt-3 text-sm text-red-700">{restoreError}</p> : null}
      </section>

      {pendingRestore ? (
        <RestoreConfirm
          manifest={pendingRestore.manifest}
          onCancel={() => setPendingRestore(null)}
          onConfirm={() => void confirmRestore()}
        />
      ) : null}
    </div>
  );
}

function RestoreConfirm({
  manifest,
  onCancel,
  onConfirm,
}: {
  manifest: BackupManifest;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <div className="mt-6 rounded-2xl border border-amber-300 bg-amber-50 p-5">
      <h3 className="font-semibold text-stone-900">Replace all learner data?</h3>
      <p className="mt-2 text-sm text-stone-700">
        Backup from {new Date(manifest.exportTimestamp).toLocaleString()} · schema v
        {manifest.databaseSchemaVersion} · content v{manifest.contentVersion}
      </p>
      <p className="mt-2 text-xs text-stone-600 break-all">
        SHA-256: {manifest.databaseChecksumSha256.slice(0, 16)}…
      </p>
      <div className="mt-4 flex gap-2">
        <button
          type="button"
          className="flex-1 rounded-xl bg-red-600 py-2 text-sm font-semibold text-white"
          onClick={onConfirm}
        >
          Restore
        </button>
        <button
          type="button"
          className="flex-1 rounded-xl border border-stone-300 py-2 text-sm"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}