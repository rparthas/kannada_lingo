# tauri-plugin-native-audio

Native phrase playback and learner recording for Kannada Quest on iOS (AVFoundation).

Invoked from TypeScript via `NativeIosAudioService` (`plugin:native-audio|*` commands). Desktop builds register the plugin but keep using `WebAudioService` in the webview.