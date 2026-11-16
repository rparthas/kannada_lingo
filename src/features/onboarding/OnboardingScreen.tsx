import { useState } from "react";
import { tauriApi } from "../../services/api/tauri";

interface Props {
  onDone: () => void;
}

export function OnboardingScreen({ onDone }: Props) {
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);

  async function finish() {
    setBusy(true);
    try {
      await tauriApi.completeOnboarding(name.trim() || undefined);
      onDone();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-dvh flex-col justify-center bg-gradient-to-b from-amber-50 to-stone-100 px-6">
      <h1 className="text-3xl font-bold text-stone-900">Kannada Quest</h1>
      <p className="mt-3 text-stone-700">
        Learn practical spoken Bengaluru Kannada in short daily sessions.
      </p>
      <label className="mt-8 block text-sm font-medium text-stone-600">
        Your name (optional)
        <input
          className="mt-2 w-full rounded-xl border border-stone-300 bg-white px-4 py-3"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Learner"
        />
      </label>
      <button
        type="button"
        disabled={busy}
        className="mt-6 rounded-xl bg-amber-500 py-3 text-lg font-semibold text-white disabled:opacity-60"
        onClick={() => void finish()}
      >
        Start learning
      </button>
    </div>
  );
}