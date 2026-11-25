const COMMANDS: &[&str] = &[
  "play_phrase",
  "pause_playback",
  "start_recording",
  "stop_recording",
  "play_learner_recording",
];

fn main() {
  tauri_plugin::Builder::new(COMMANDS)
    .android_path("android")
    .ios_path("ios")
    .build();
}