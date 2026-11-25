import AVFoundation
import Foundation
import Tauri

private struct PlayPhraseArgs: Decodable {
  let filePath: String
  let speed: String?
}

private struct PlayLearnerArgs: Decodable {
  let filePath: String
}

private struct RecordingResultPayload: Encodable {
  let filePath: String
  let durationMs: Int
}

class NativeAudioPlugin: Plugin {
  private var phrasePlayer: AVAudioPlayer?
  private var learnerPlayer: AVAudioPlayer?
  private var recorder: AVAudioRecorder?
  private var recordingStartedAt: Date?

  private func activatePlaybackSession() throws {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
    try session.setActive(true)
  }

  private func activateRecordingSession() throws {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(
      .playAndRecord,
      mode: .spokenAudio,
      options: [.defaultToSpeaker, .allowBluetooth],
    )
    try session.setActive(true)
  }

  private func micDeniedMessage() -> String {
    "Microphone access is off. Open Settings → Kannada Quest and turn on Microphone, then try again."
  }

  private func ensureMicPermission(_ completion: @escaping (Result<Void, String>) -> Void) {
    let session = AVAudioSession.sharedInstance()
    switch session.recordPermission {
    case .granted:
      completion(.success(()))
    case .denied:
      completion(.failure(self.micDeniedMessage()))
    case .undetermined:
      session.requestRecordPermission { granted in
        DispatchQueue.main.async {
          if granted {
            completion(.success(()))
          } else {
            completion(.failure(self.micDeniedMessage()))
          }
        }
      }
    @unknown default:
      completion(.failure(self.micDeniedMessage()))
    }
  }

  @objc public func playPhrase(_ invoke: Invoke) throws {
    let args = try invoke.parseArgs(PlayPhraseArgs.self)
    let url = URL(fileURLWithPath: args.filePath)
    guard FileManager.default.fileExists(atPath: url.path) else {
      invoke.reject("Audio file is missing. Rebuild and reinstall the app.")
      return
    }
    try activatePlaybackSession()
    phrasePlayer?.stop()
    learnerPlayer?.stop()
    let player = try AVAudioPlayer(contentsOf: url)
    player.enableRate = true
    let speed = args.speed ?? "normal"
    player.rate = speed == "slow" ? 0.82 : 1.0
    player.prepareToPlay()
    phrasePlayer = player
    if !player.play() {
      invoke.reject("Could not start playback.")
      return
    }
    invoke.resolve()
  }

  @objc public func pausePlayback(_ invoke: Invoke) throws {
    phrasePlayer?.stop()
    phrasePlayer = nil
    learnerPlayer?.stop()
    learnerPlayer = nil
    invoke.resolve()
  }

  @objc public func startRecording(_ invoke: Invoke) throws {
    ensureMicPermission { result in
      switch result {
      case .failure(let message):
        invoke.reject(message)
      case .success:
        do {
          try self.activateRecordingSession()
          let dir = try self.learnerRecordingDirectory()
          let fileName = "\(UUID().uuidString).m4a"
          let fileURL = dir.appendingPathComponent(fileName)
          let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44_100,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue,
          ]
          let recorder = try AVAudioRecorder(url: fileURL, settings: settings)
          recorder.prepareToRecord()
          self.recordingStartedAt = Date()
          self.recorder = recorder
          if !recorder.record() {
            invoke.reject("Could not start recording.")
            return
          }
          invoke.resolve()
        } catch {
          invoke.reject("Could not start recording: \(error.localizedDescription)")
        }
      }
    }
  }

  @objc public func stopRecording(_ invoke: Invoke) throws {
    guard let recorder = recorder else {
      invoke.reject("No recording in progress.")
      return
    }
    let startedAt = recordingStartedAt ?? Date()
    recorder.stop()
    self.recorder = nil
    recordingStartedAt = nil
    let durationMs = Int(Date().timeIntervalSince(startedAt) * 1000)
    let payload = RecordingResultPayload(
      filePath: recorder.url.path,
      durationMs: max(durationMs, 0),
    )
    invoke.resolve(payload)
  }

  @objc public func playLearnerRecording(_ invoke: Invoke) throws {
    let args = try invoke.parseArgs(PlayLearnerArgs.self)
    let url = URL(fileURLWithPath: args.filePath)
    guard FileManager.default.fileExists(atPath: url.path) else {
      invoke.reject("Recording file is missing.")
      return
    }
    try activatePlaybackSession()
    phrasePlayer?.stop()
    learnerPlayer?.stop()
    let player = try AVAudioPlayer(contentsOf: url)
    player.prepareToPlay()
    learnerPlayer = player
    if !player.play() {
      invoke.reject("Could not play your recording.")
      return
    }
    invoke.resolve()
  }

  private func learnerRecordingDirectory() throws -> URL {
    let docs = try FileManager.default.url(
      for: .documentDirectory,
      in: .userDomainMask,
      appropriateFor: nil,
      create: true,
    )
    let dir = docs.appendingPathComponent("learner_recordings", isDirectory: true)
    try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
    return dir
  }
}

@_cdecl("init_plugin_native_audio")
public func initPlugin() -> Plugin {
  return NativeAudioPlugin()
}