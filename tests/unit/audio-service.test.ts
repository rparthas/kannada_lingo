import { describe, expect, it } from "vitest";
import {
  resolveAudioServiceKind,
  type AudioServiceKind,
} from "../../src/services/audio/platform";

describe("resolveAudioServiceKind", () => {
  const cases: Array<{
    isTauri: boolean;
    platform: string;
    expected: AudioServiceKind;
  }> = [
    { isTauri: false, platform: "web", expected: "stub" },
    { isTauri: true, platform: "ios", expected: "native-ios" },
    { isTauri: true, platform: "macos", expected: "web" },
    { isTauri: true, platform: "windows", expected: "web" },
  ];

  it.each(cases)(
    "picks $expected when isTauri=$isTauri and platform=$platform",
    ({ isTauri, platform, expected }) => {
      expect(resolveAudioServiceKind({ isTauri, platform })).toBe(expected);
    },
  );
});