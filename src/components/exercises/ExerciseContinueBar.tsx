interface Props {
  feedback: string;
  isCorrect: boolean;
  explanation?: string;
  onContinue: () => void;
}

export function ExerciseContinueBar({
  feedback,
  isCorrect,
  explanation,
  onContinue,
}: Props) {
  return (
    <div
      className={`space-y-3 rounded-2xl p-4 ${isCorrect ? "bg-emerald-50 ring-1 ring-emerald-200" : "bg-amber-50 ring-1 ring-amber-200"}`}
    >
      <div className="flex items-center gap-3">
        {isCorrect ? (
          <svg
            className="h-6 w-6 flex-shrink-0 text-emerald-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        ) : null}
        <p className="font-medium text-stone-900">{feedback}</p>
      </div>
      {explanation ? <p className="text-sm text-stone-600">{explanation}</p> : null}
      <button
        type="button"
        className="w-full rounded-xl bg-stone-900 py-3 font-semibold text-white"
        onClick={onContinue}
      >
        Continue
      </button>
    </div>
  );
}