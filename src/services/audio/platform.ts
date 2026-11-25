export type AudioServiceKind = "stub" | "web" | "native-ios";

export function resolveAudioServiceKind(input: {
  isTauri: boolean;
  platform: string;
}): AudioServiceKind {
  if (!input.isTauri) return "stub";
  if (input.platform === "ios") return "native-ios";
  return "web";
}