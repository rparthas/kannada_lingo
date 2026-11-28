import { useMemo, useState } from "react";
import type { ExerciseDto, LearningItemDto } from "../../services/api/tauri";
import {
  evaluateKannadaRecall,
  evaluateMultipleChoice,
  evaluateWordOrder,
  normalizeFreeText,
} from "../../domain/exercises/evaluate";
import { ExerciseContinueBar } from "./ExerciseContinueBar";
import { LearnerRecordingPanel } from "../audio/LearnerRecordingPanel";
import { PhraseAudioControls } from "../audio/PhraseAudioControls";

export interface ExerciseResult {
  isCorrect: boolean;
  response: Record<string, unknown>;
  selfAssessed?: boolean;
}

interface Props {
  exercise: ExerciseDto;
  onComplete: (result: ExerciseResult) => void;
}

interface ConversationChoice {
  label: string;
  hint?: string;
  correct: boolean;
}

interface ConversationStep {
  narration?: string;
  partner?: {
    kannada: string;
    transliteration: string;
    english: string;
  };
  choices?: ConversationChoice[];
  explanation?: string;
}

function PhraseCard({
  item,
  showText = true,
  showAudio = false,
}: {
  item: LearningItemDto;
  showText?: boolean;
  showAudio?: boolean;
}) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-stone-200 space-y-3">
      {showText ? (
        <>
          <p className="text-3xl font-semibold text-stone-900 kannada">{item.kannadaText}</p>
          <p className="mt-2 text-lg text-amber-800">{item.transliteration}</p>
        </>
      ) : (
        <p className="text-sm font-medium text-stone-500">Listen carefully before you answer.</p>
      )}
      {showAudio ? (
        <PhraseAudioControls
          learningItemId={item.id}
          compact={!showText}
          autoPlay={!showText}
        />
      ) : null}
      {item.contextNote && showText ? (
        <p className="mt-3 text-sm text-stone-600">{item.contextNote}</p>
      ) : null}
    </div>
  );
}

export function ExerciseRenderer({ exercise, onComplete }: Props) {
  const item = exercise.learningItem;
  const [revealed, setRevealed] = useState(false);
  const [textAnswer, setTextAnswer] = useState("");
  const [selected, setSelected] = useState<number | null>(null);
  const [tiles, setTiles] = useState<string[]>(
    () => (exercise.prompt.tiles as string[] | undefined)?.slice() ?? [],
  );
  const [built, setBuilt] = useState<string[]>([]);
  const [pending, setPending] = useState<{
    result: ExerciseResult;
    message: string;
    explanation?: string;
  } | null>(null);

  const choices = useMemo(
    () => (exercise.prompt.choices as string[] | undefined) ?? [],
    [exercise.prompt.choices],
  );

  function queueResult(
    result: ExerciseResult,
    message: string,
    explanation?: string,
  ) {
    setPending({ result, message, explanation });
  }

  function submitMcq(correctIndex: number) {
    if (selected === null) return;
    const isCorrect = evaluateMultipleChoice(selected, correctIndex);
    queueResult(
      { isCorrect, response: { selected } },
      isCorrect ? "Correct" : "Not quite — check the meaning again.",
      isCorrect ? undefined : "Review the phrase card before you continue.",
    );
  }

  /** Check and Continue share one slot, so the button turns into the next step. */
  function submitArea(
    label: string,
    disabled: boolean,
    onClick: () => void,
  ) {
    if (pending) {
      return (
        <ExerciseContinueBar
          feedback={pending.message}
          isCorrect={pending.result.isCorrect}
          explanation={pending.explanation}
          onContinue={() => onComplete(pending.result)}
        />
      );
    }
    return (
      <button
        type="button"
        className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white disabled:opacity-50"
        disabled={disabled}
        onClick={onClick}
      >
        {label}
      </button>
    );
  }

  if (!item && exercise.exerciseType !== "vocabulary_flashcard" && exercise.exerciseType !== "scripted_conversation") {
    return <p className="text-stone-600">Exercise is missing phrase data.</p>;
  }

  const instruction = String(exercise.prompt.instruction ?? "Complete the exercise.");

  switch (exercise.exerciseType) {
    case "vocabulary_flashcard":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} showAudio />
          {!revealed ? (
            <button
              type="button"
              className="w-full rounded-xl bg-amber-500 py-3 font-semibold text-white"
              onClick={() => setRevealed(true)}
            >
              Reveal meaning
            </button>
          ) : (
            <div className="space-y-3">
              <p className="text-xl font-medium text-stone-900">{item.englishMeaning}</p>
              <button
                type="button"
                className="w-full rounded-xl bg-stone-900 py-3 font-semibold text-white"
                onClick={() =>
                  onComplete({ isCorrect: true, response: { revealed: true } })
                }
              >
                Continue
              </button>
            </div>
          )}
        </div>
      );

    case "listen_identify":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} showText={false} showAudio />
          <div className="grid gap-2">
            {choices.map((choice, index) => (
              <button
                key={choice}
                type="button"
                disabled={!!pending}
                className={`rounded-xl border px-4 py-3 text-left ${
                  selected === index ? "border-amber-500 bg-amber-50" : "border-stone-200"
                }`}
                onClick={() => setSelected(index)}
              >
                {choice}
              </button>
            ))}
          </div>
          {submitArea("Check", selected === null, () =>
            submitMcq(Number(exercise.prompt.correct_index ?? exercise.prompt.correctIndex)),
          )}
        </div>
      );

    case "kannada_to_english":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} showAudio />
          <div className="grid gap-2">
            {choices.map((choice, index) => (
              <button
                key={choice}
                type="button"
                disabled={!!pending}
                className={`rounded-xl border px-4 py-3 text-left ${
                  selected === index ? "border-amber-500 bg-amber-50" : "border-stone-200"
                }`}
                onClick={() => setSelected(index)}
              >
                {choice}
              </button>
            ))}
          </div>
          {submitArea("Check", selected === null, () =>
            submitMcq(Number(exercise.prompt.correct_index ?? exercise.prompt.correctIndex)),
          )}
        </div>
      );

    case "english_to_kannada":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <p className="text-xl font-medium">{item.englishMeaning}</p>
          <input
            className="w-full rounded-xl border border-stone-300 px-4 py-3 text-lg"
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            placeholder="Type Kannada or transliteration"
            autoCapitalize="off"
            autoCorrect="off"
            disabled={!!pending}
          />
          {submitArea("Check", false, () => {
            const isCorrect = evaluateKannadaRecall(textAnswer, {
              kannadaText: item.kannadaText,
              transliteration: item.transliteration,
              englishMeaning: item.englishMeaning,
              acceptedAnswers: item.acceptedAnswers,
            });
            queueResult(
              { isCorrect, response: { textAnswer } },
              isCorrect ? "Correct" : "Keep practising this one.",
              isCorrect
                ? undefined
                : `Expected something like “${item.transliteration}”.`,
            );
          })}
        </div>
      );

    case "fill_blank": {
      if (!item) return null;
      const accepted =
        (exercise.prompt.accepted as string[] | undefined) ?? [];
      const blanked = String(exercise.prompt.blanked_transliteration ?? "");
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <p className="text-lg text-stone-800">{blanked}</p>
          <input
            className="w-full rounded-xl border border-stone-300 px-4 py-3"
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            disabled={!!pending}
          />
          {submitArea("Check", false, () => {
            const isCorrect = [item.transliteration, ...accepted].some(
              (v) => normalizeFreeText(textAnswer) === normalizeFreeText(v),
            );
            queueResult(
              { isCorrect, response: { textAnswer } },
              isCorrect ? "Correct" : "That blank needs another try.",
            );
          })}
        </div>
      );
    }

    case "sentence_construction": {
      const solution =
        (exercise.prompt.solution as string[] | undefined) ?? [];
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <div className="min-h-12 rounded-xl border border-dashed border-stone-300 p-3">
            {built.length === 0 ? (
              <span className="text-stone-400">Tap words in order</span>
            ) : (
              built.join(" ")
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {tiles.map((tile) => (
              <button
                key={tile}
                type="button"
                disabled={!!pending}
                className="rounded-full bg-stone-100 px-4 py-2 text-sm"
                onClick={() => {
                  setBuilt((prev) => [...prev, tile]);
                  setTiles((prev) => prev.filter((t) => t !== tile));
                }}
              >
                {tile}
              </button>
            ))}
          </div>
          {submitArea("Check order", built.length === 0, () => {
            const isCorrect = evaluateWordOrder(built, solution);
            queueResult(
              { isCorrect, response: { built } },
              isCorrect ? "Correct order" : "Word order is not quite right.",
              isCorrect ? undefined : `Solution: ${solution.join(" ")}`,
            );
          })}
        </div>
      );
    }

    case "listen_repeat":
      if (!item) return null;
      return (
        <div className="space-y-4">
          <p className="text-stone-700">{instruction}</p>
          <PhraseCard item={item} showAudio />
          <LearnerRecordingPanel />
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Needs practice", ok: false, confident: false },
              { label: "Good", ok: true, confident: false },
              { label: "Easy", ok: true, confident: true },
            ].map((opt) => (
              <button
                key={opt.label}
                type="button"
                className="rounded-xl border border-stone-200 py-3 text-sm"
                onClick={() =>
                  onComplete({
                    isCorrect: opt.ok,
                    selfAssessed: opt.confident,
                    response: { selfGrade: opt.label },
                  })
                }
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      );

    case "scripted_conversation":
      return (
        <ScriptedConversation
          instruction={instruction}
          steps={(exercise.prompt.steps as ConversationStep[] | undefined) ?? []}
          onComplete={onComplete}
        />
      );

    default:
      return (
        <p className="text-stone-600">Unsupported exercise type: {exercise.exerciseType}</p>
      );
  }
}

function ScriptedConversation({
  instruction,
  steps,
  onComplete,
}: {
  instruction: string;
  steps: ConversationStep[];
  onComplete: (result: ExerciseResult) => void;
}) {
  const [stepIndex, setStepIndex] = useState(0);
  const [wrongChoice, setWrongChoice] = useState<string | null>(null);
  const [hadWrong, setHadWrong] = useState(false);

  const step = steps[stepIndex];
  if (!step) {
    return <p className="text-stone-600">Conversation has no steps.</p>;
  }

  function advance() {
    setWrongChoice(null);
    if (stepIndex + 1 >= steps.length) {
      onComplete({
        isCorrect: !hadWrong,
        response: { stepsCompleted: steps.length, hadWrong },
      });
      return;
    }
    setStepIndex((i) => i + 1);
  }

  if (step.partner) {
    return (
      <div className="space-y-4">
        <p className="text-stone-700">{instruction}</p>
        {step.narration ? (
          <p className="text-sm font-medium text-stone-500">{step.narration}</p>
        ) : null}
        <div className="rounded-2xl bg-white p-5 ring-1 ring-stone-200">
          <p className="text-sm text-stone-500">Partner</p>
          <p className="text-3xl font-semibold kannada">{step.partner.kannada}</p>
          <p className="mt-2 text-lg text-amber-800">{step.partner.transliteration}</p>
          <p className="mt-2 text-stone-700">{step.partner.english}</p>
        </div>
        <button
          type="button"
          className="w-full rounded-xl bg-stone-900 py-3 font-semibold text-white"
          onClick={advance}
        >
          Continue
        </button>
      </div>
    );
  }

  const choiceStep = step;
  return (
    <div className="space-y-4">
      <p className="text-stone-700">{instruction}</p>
      {choiceStep.narration ? (
        <p className="text-sm font-medium text-stone-500">{choiceStep.narration}</p>
      ) : null}
      <div className="grid gap-2">
        {(choiceStep.choices ?? []).map((choice) => (
          <button
            key={choice.label}
            type="button"
            className={`rounded-xl border px-4 py-3 text-left ${
              wrongChoice === choice.label
                ? "border-red-300 bg-red-50"
                : "border-stone-200"
            }`}
            onClick={() => {
              if (choice.correct) {
                advance();
              } else {
                setHadWrong(true);
                setWrongChoice(choice.label);
              }
            }}
          >
            <span className="font-medium">{choice.label}</span>
            {choice.hint ? (
              <span className="mt-1 block text-sm text-stone-500">{choice.hint}</span>
            ) : null}
          </button>
        ))}
      </div>
      {wrongChoice && choiceStep.explanation ? (
        <p className="rounded-xl bg-amber-50 p-3 text-sm text-stone-700">
          {choiceStep.explanation}
        </p>
      ) : null}
    </div>
  );
}