import { open } from "@tauri-apps/plugin-dialog";
import { tauriApi } from "../../services/api/tauri";

export function SettingsScreen() {
  async function importBackup() {
    const file = await open({
      multiple: false,
      filters: [{ name: "Kannada Quest Backup", extensions: ["zip", "kqbackup.zip"] }],
    });
    if (!file || typeof file !== "string") return;
    await tauriApi.validateLearningBackup(file);
    await tauriApi.restoreLearningBackup(file);
    window.location.reload();
  }

  return (
    <div className="mx-auto max-w-3xl px-4 pb-28 pt-4">
      <h1 className="text-2xl font-bold text-stone-900">Settings</h1>
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
      </section>
    </div>
  );
}