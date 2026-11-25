use tauri::{
  plugin::{Builder, TauriPlugin},
  Manager, Runtime,
};

pub use models::*;

#[cfg(desktop)]
mod desktop;
#[cfg(mobile)]
mod mobile;

mod commands;
mod error;
mod models;

pub use error::{Error, Result};

#[cfg(desktop)]
use desktop::NativeAudio;
#[cfg(mobile)]
use mobile::NativeAudio;

/// Extensions to [`tauri::App`], [`tauri::AppHandle`] and [`tauri::Window`] to access the native-audio APIs.
pub trait NativeAudioExt<R: Runtime> {
  fn native_audio(&self) -> &NativeAudio<R>;
}

impl<R: Runtime, T: Manager<R>> crate::NativeAudioExt<R> for T {
  fn native_audio(&self) -> &NativeAudio<R> {
    self.state::<NativeAudio<R>>().inner()
  }
}

/// Initializes the plugin.
pub fn init<R: Runtime>() -> TauriPlugin<R> {
  Builder::new("native-audio")
    .invoke_handler(tauri::generate_handler![
      commands::play_phrase,
      commands::pause_playback,
      commands::start_recording,
      commands::stop_recording,
      commands::play_learner_recording,
    ])
    .setup(|app, api| {
      #[cfg(mobile)]
      let native_audio = mobile::init(app, api)?;
      #[cfg(desktop)]
      let native_audio = desktop::init(app, api)?;
      app.manage(native_audio);
      Ok(())
    })
    .build()
}