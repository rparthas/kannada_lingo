import { describe, expect, it } from "vitest";
import { gradeFromAttempt, scheduleReview } from "../../src/domain/revision/sm2";

describe("scheduleReview", () => {
  it("resets on failure", () => {
    const next = scheduleReview(
      { easeFactor: 2.5, intervalDays: 10, repetitions: 4 },
      0,
    );
    expect(next.repetitions).toBe(0);
    expect(next.intervalDays).toBe(0);
    expect(next.masteryStatus).toBe("learning");
  });

  it("grows interval on success", () => {
    const first = scheduleReview(
      { easeFactor: 2.5, intervalDays: 0, repetitions: 0 },
      4,
    );
    expect(first.intervalDays).toBe(1);
    const second = scheduleReview(first, 4);
    expect(second.intervalDays).toBe(3);
    const third = scheduleReview(second, 5);
    expect(third.intervalDays).toBeGreaterThanOrEqual(7);
  });
});

describe("gradeFromAttempt", () => {
  it("maps self-assessed speaking", () => {
    expect(gradeFromAttempt({ isCorrect: true, selfAssessedConfident: true })).toBe(5);
    expect(gradeFromAttempt({ isCorrect: false })).toBe(0);
  });
});