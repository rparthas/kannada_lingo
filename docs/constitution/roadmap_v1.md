# **Kannada Quest — Speaking-First Product Roadmap**

# **Product direction**

Approved direction

**Build a personal Kannada speaking coach for everyday conversations in Bengaluru.**

The primary learning loop:

**LISTEN**

Hear natural Bengaluru Kannada

**UNDERSTAND**

Learn meaning, context and usage

**SPEAK**

Respond without looking at the answer

**GET FEEDBACK**

Identify mistakes and learn natural expressions

**RETAIN**

Practice again through spaced repetition

**Product constraints**

- Personal-first, single learner.
- iPhone-first, with iPad support.
- English as the teaching language.
- Hybrid audio: human recordings where quality matters, generated audio elsewhere.
- Content-assisted AI, not AI-generated canonical curriculum.
- Tauri 2 + React + Rust + SQLite.
- Offline-first, with optional AI connectivity.
- No mandatory accounts or cloud backend for core learning.

This preserves the decisions already established for Kannada Quest.&#x20;

## **1. Strategic priorities**

I would organize the roadmap around five capabilities rather than a collection of unrelated features.

| Capability                       | Priority | Product outcome                                 |
| -------------------------------- | -------- | ----------------------------------------------- |
| Speaking practice engine         | P0       | Speak phrases without reading                   |
| Speech recognition and feedback  | P0       | Know whether the spoken response was understood |
| Real-life conversation simulator | P0       | Handle everyday situations                      |
| Intelligent revision             | P1       | Remember and recall phrases                     |
| AI conversation coach            | P1       | Have less predictable conversations             |

The important distinction: speech recognition, pronunciation evaluation and conversation intelligence are three different capabilities. We should build them separately.

For example, recognizing that you said "namaskara" does not establish that you pronounced it naturally. Don't conflate transcription accuracy with pronunciation quality.

# **2. Detailed roadmap**

## **Release 0 — Strengthen the speaking foundation**

P0 · First release

**Objective:** Make the existing recording and listening experience reliable on your actual iPhone.

Your repository already has:

- `NativeIosAudioService`
- `LearnerRecordingPanel`
- Normal and slow phrase playback.
- `listen_repeat` exercises.
- Swift native audio plugin.

However, physical-device verification remains open in the existing feature specification.&#x20;

repomix-output(2).md



### **Features**

**A. Speaking practice mode**

Add a dedicated speaking exercise:

1. Play a Kannada phrase.
2. Hide its transliteration and English meaning.
3. Ask the learner to repeat it.
4. Record the learner.
5. Replay the recording.
6. Let the learner rate their attempt.
7. Add the phrase to revision scheduling.

**B. Recording improvements**

- Record, stop, replay and retry.
- Preserve recordings across app navigation during an exercise.
- Clear microphone permission guidance.
- Handle interruptions and audio session changes.
- Provide visual recording feedback.

**C. Speaking progress**

Track:

- Number of phrases spoken.
- Number of speaking attempts.
- Self-rated difficulty.
- Phrases requiring more practice.

### **Acceptance criteria**

- Normal and slow playback work on physical iPhone.
- Recording and playback work repeatedly.
- Microphone denial and recovery work.
- No recording is lost during normal exercise navigation.
- Core functionality works offline.

**Deliverable:** A reliable speaking practice experience, not just a phrase-listening application.

## **Release 1 — Speech recognition and speaking feedback**

P0 · Core differentiator

**Objective:** Replace self-assessment with measurable feedback.

[Elsa Speak vs Duolingo: Sự Khác Biệt Bạn Cần Biết Khi Học Tiếng Anh](https://images.openai.com/static-rsc-4/7zkbZ6hLNpw3jf3JEL6Yqtc_NaptG4vh5MmaGS_FQ5vKZmu36Xd40kl2cXMRWeGHqgMd2HAnNZEZ8JX-OETu576toJZdQo0VgcHJahKjQaJUQrnSZOaTaKsbHVLyA-V3LJkpqqNB4ZyxJb1tX-dnJ9-si9sdP7tqWQq6KRowJ4Q?purpose=inline)

[sadesign.vn](https://sadesign.vn/elsa-speak-duolingo-su-khac-biet?utm_source=chatgpt.com)

### **Feature specification**

Introduce a speech recognition abstraction.

```
interface SpeechRecognitionService {
  isAvailable(): Promise<boolean>;

  startRecognition(): Promise<void>;

  stopRecognition(): Promise<{
    transcript: string;
    confidence?: number;
  }>;
}
```

The iOS implementation can use Apple's native Speech framework through a Swift/Tauri integration.

Keep this separate from your existing audio playback and recording service.

### **Learner experience**

Example target phrase:

TARGET PHRASE

# **ನಮಸ್ಕಾರ**

**namaskāra**\
Hello

**Your response**

Recognized

# **Namaskara**

Illustrative recognition result

**Feedback**

- The phrase was recognized.
- Try listening to the natural-speed version.
- Repeat without looking at the transliteration.

### **Features to implement**

1. Convert speech to Kannada text.
2. Normalize Kannada and transliteration variants.
3. Compare recognized text against accepted answers.
4. Highlight missing or substituted words.
5. Allow another attempt.
6. Store recognition outcome and attempt history.
7. Provide keyboard fallback if speech recognition is unavailable.

### **Important technical distinction**

Build three separate evaluation levels:

| Level         | What it measures                             | Initial implementation      |
| ------------- | -------------------------------------------- | --------------------------- |
| Recognition   | Did the system understand the phrase?        | Speech-to-text              |
| Recall        | Did the learner produce the expected phrase? | Answer comparison           |
| Pronunciation | Was the pronunciation natural and accurate?  | Later, dedicated assessment |

Do not claim pronunciation accuracy based solely on speech-to-text.

### **Acceptance criteria**

- Recognition works for supported Kannada phrases.
- Accepted alternatives are respected.
- Recognition failures don't automatically penalize the learner.
- Manual input remains available.
- Offline availability is detected rather than assumed.
- No recordings are transmitted to external services.

**Deliverable:** Speaking exercises with useful feedback.

## **Release 2 — Real-life conversation simulator**

P0 · Highest product value

**Objective:** Move from repeating isolated phrases to responding in conversations.

[Frontiers | Mobile language app learners’ self-efficacy increases after using generative AI](https://images.openai.com/static-rsc-4/3ORQfcdqiEzUVB064rOhqM2-uJyCm9kZIk7yrrZlycwYyL_wXDRaf4JmBRWFePHYWxEOfbP1Vw4cNt_fgN8f3HdK6GUvhDcZnBgzRxMGmNB3uPMhLleOwwAoqpqRswV4oh5f1vtcLQmzNZFbuJBuXnUNHf5FURGwYriwXFsVWAM?purpose=inline)

[frontiersin.org](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1499497/full?utm_source=chatgpt.com)

This is where I think Kannada Quest can become genuinely useful.

### **Feature specification**

Create a new learning mode called **Conversation Practice**.

Start with these scenarios:

[Karnataka government orders action against app-based and other auto-rickshaws for overcharging in Bengaluru, ETAuto](https://images.openai.com/static-rsc-4/6j_j3HXQgFAMKkuSrSMmSUSTxvIhnyVH3m58tGBzXvnYQnnu2HtpdphfsiWZbSA0i_l3TDOHVLGNec8DtGsbhZ-1AxPMVzPiGND3mrACKcyI7HJ4wPDo8MhPh6DQLZVou95I7MVmTVKEZNXcJDy8W_k585N-d0mGdOlg1oolDo8?purpose=inline)

**Auto driver**

Destination, fare, directions and stops

[Must Visit in Bangalore | Brahmins Coffee Bar - Tripoto](https://images.openai.com/static-rsc-4/EycQaAB5a_rNOhabE5RefJS7PNZFyVsBGdRhfyIi5cbFyvatx3gEXdraavL2FFzP3HV7Omtz1lEjQFcwxBCl86bTDVYDS4NtEwOObm_8u4Us4kdVmktS33qCFWCLmpL6cVgn9yEejCj6-GOFECe2yJ2pAwuKEvGeGHkzGYEIY7w?purpose=inline)

**Restaurant**

Ordering, preferences and payment

[Our Services | Dhruva Global Security Bengaluru](https://images.openai.com/static-rsc-4/Xjy2rZNYpUAppZaLIcYHb09cMJy3DQ69vzK72OW6vL5gJwvXsu0UY4RmwelcZA7yL7q1SUG2_wppFzWIyywg5VNhQXHfirDvwkWRXi2Lbo-K8-xMCoWQbkcuPcD__cH-MQ4nvf6kCxyL9XCZK5k74pcg0ckPU4ItfZRnoy6LewA?purpose=inline)

**Apartment security**

Visitors, deliveries and directions

[Most of India still chooses to use kirana stores](https://images.openai.com/static-rsc-4/R7N2PbO-XrqLRTkRm7YupLXlj5kfhZnljLtZyzZA3gcBLp0JiQ1VOUCvnzzoaSHl2frBbXQUoIZjsT86NViR3uKwDqwTYBJhHIwoXy0biHtfRmdUDmplqTXmgm1PIoTGdbjdgUIpO0KPxzpP0B2L1IK4CbJZITxuG-N5B-v-sSk?purpose=inline)

**Shopkeeper**

Prices, quantities and availability

['Why Bengaluru landlords are such crap': Tenant living in a one-room kitchen apartment sparks debate on unfair charges - The Economic Times](https://images.openai.com/static-rsc-4/4qYtMfiMlJIVcpTfBybojvyvRc9B8BskT2Hb9DFen9eZ4QVs58noxPq4uTKN36dadx2RogJTk6Um1qB9ac0iJffhKo5F4RVFrd3xCBwmpq3A8UQI9NWdS0t16LU17wblz5vqwGoc5_SFlbFfFgdvNZ7o0x6QDgYIQPz-O3o06yg?purpose=inline)

**Neighbour**

Greetings, small talk and invitations

### **Conversation flow**

Example: Ordering food.

1. App plays: "ಏನು ಬೇಕು?" (What would you like?)
2. You respond verbally.
3. Speech recognition transcribes your answer.
4. The application checks whether your response is contextually appropriate.
5. The next conversation step is selected.
6. At the end, you receive feedback.

### **Conversation engine architecture**

Start with deterministic, content-defined conversations.

```
interface ConversationScenario {
  id: string;
  title: string;
  situation: string;
  difficulty: number;
  steps: ConversationStep[];
}

interface ConversationStep {
  partnerPhraseId?: string;
  expectedIntents: string[];
  acceptedPhraseIds: string[];
  fallbackHint?: string;
}
```

The scenario engine should:

- Support multiple acceptable answers.
- Support alternate dialogue branches.
- Provide hints after failed attempts.
- Explain why an answer is appropriate.
- Track successful completion.

Reuse your existing `scripted_conversation` content where appropriate, but don't force all conversations into the existing multiple-choice model.

### **Acceptance criteria**

- At least five complete scenarios.
- At least three valid response paths per scenario where relevant.
- Spoken answers accepted through speech recognition.
- Typed fallback available.
- Conversations work offline using bundled content and audio.
- Completion records are stored locally.

**Deliverable:** A practical conversational simulator.

## **Release 3 — AI conversation coach**

P1 · Major capability

**Objective:** Make conversations less predictable and more natural.

[Univerbal - AI Tool for Language Learning | AIAXIO](https://images.openai.com/static-rsc-4/KL5q1yJJdN4yfuDHAXzzFUrpURFM4jXgs3ChbFVEJ0-VrFLsAb_7hQTXVhoLJMzVquL3WjUyibg4TOCT8CnMTGcD9X8X99iZIzgBlZYcI2Et9UA5nHHu4rvp9RXMp1TCyANq2sKc2xAc8JrqLERUxZs0JzAb_DrGuNOIx03rhLA?purpose=inline)

[aiaxio.com](https://aiaxio.com/tools/ai/univerbal/?utm_source=chatgpt.com)

Once the deterministic conversation engine works, introduce AI.

I would not start with an unrestricted chatbot. That would make language quality difficult to control.

### **Feature specification**

The AI acts as a conversation partner with a defined role.

Example:

- Role: Bengaluru auto driver.
- Learner level: Beginner.
- Language: Spoken Bengaluru Kannada.
- Teaching language: English.
- Difficulty: Beginner.
- Expected learner response: Kannada.
- Feedback: English.

### **Three modes**

| Mode      | Behaviour                                              |
| --------- | ------------------------------------------------------ |
| Guided    | AI provides hints and suggested phrases                |
| Normal    | AI responds naturally and corrects mistakes afterwards |
| Challenge | AI speaks Kannada without showing translations         |

### **Feedback after each conversation**

Show:

1. What you communicated successfully.
2. Grammar mistakes.
3. More natural Bengaluru Kannada alternatives.
4. New vocabulary.
5. Phrases worth revisiting.

For example:

- You said: `nanu coffee beku`
- Suggested: `nanage coffee beku`
- Explanation: The suggested expression is a more natural way to express wanting coffee.

The actual correction should be validated against the intended meaning and reviewed language patterns, not treated as a universal grammar rule.

### **Architecture**

**Conversation UI**

**Speech Recognition Service**

**Conversation Orchestrator**

**Context Builder**

Learner level · Scenario · Approved phrases · Grammar patterns

**AI Provider**

**Response Validation**

**Audio Playback + Feedback**

### **Technical requirements**

- Reuse `AIContentProvider` where appropriate, but introduce a separate conversation interface.
- No API secrets in the application bundle.
- Use a backend proxy or an appropriate on-device model boundary.
- Explicit user opt-in for AI.
- Send recognized text rather than recordings by default.
- Keep AI responses separate from canonical curriculum content.
- Gracefully handle network failures.

**Acceptance criteria**

- AI can maintain context across at least 10 conversation turns.
- AI respects the assigned learner level.
- Corrections are presented in English.
- Canonical phrase content remains unchanged.
- AI is disabled by default.
- No network dependency for core lessons or revision.

**Deliverable:** An interactive Kannada conversation coach.

## **Release 4 — Listening comprehension**

P1 · Supporting capability

**Objective:** Understand Kannada when someone speaks naturally, not just when the app presents a known phrase.

[Mejores 8 aplicaciones para mejorar tu listening de inglés](https://images.openai.com/static-rsc-4/Dl1-tpNUo-y8mRhdZK6xcqFRZYkT5IfSVqH69v_wHIc6LQERDjE5QrbcBbR5WDC1ylffMXUBaSqZhAxdfBcZ04YOjKY95rpeVUU3dNnMHw6F7zT6RuZYp_jOgJrBt2N4gE7yTfE1g1-V_sEzIsiAubTPY5LPGeAJhJqVZOKOnS0?purpose=inline)

[larazon.es](https://www.larazon.es/tecnologia-consumo/aplicaciones-gratis/mejores-aplicaciones-mejorar-listening-ingles-leer-descripcion_2022052969944a0f2f00a04688127477.html?utm_source=chatgpt.com)

### **Features**

- Short two-person conversations.
- Listen without seeing the transcript.
- Identify the main meaning.
- Answer comprehension questions.
- Select an appropriate response.
- Reveal the transcript after answering.
- Replay at normal and slow speeds.

Introduce gradually:

1. Individual phrases.
2. Short sentences.
3. Two-turn conversations.
4. Longer everyday conversations.
5. Natural-speed conversational audio.

### **Acceptance criteria**

- At least 20 short dialogue exercises.
- Every dialogue has an approved transcript.
- Audio and transcript are versioned together.
- Listening exercises work offline.
- Comprehension results feed into revision.

## **Release 5 — Speaking-focused revision engine**

P1 · Retention

**Objective:** Make the existing spaced repetition system optimize for active speaking rather than passive recognition.

Your existing SM-2-inspired scheduler is a useful foundation. I would extend the learning signals rather than replace it.

### **Introduce separate skill dimensions**

| Dimension   | Example                             |
| ----------- | ----------------------------------- |
| Recognition | Understand what someone says        |
| Recall      | Remember a phrase without hints     |
| Speaking    | Produce the phrase verbally         |
| Listening   | Understand a phrase at normal speed |

A phrase could be mastered in recognition but still need speaking practice.

### **Proposed revision flow**

A daily session should contain:

- 40% speaking recall.
- 25% listening comprehension.
- 20% phrase recognition.
- 15% conversation practice.

These are starting configuration values, not fixed pedagogical truths. Adjust them based on observed learning performance.

### **Acceptance criteria**

- Separate performance history by exercise type.
- Prioritize weak speaking phrases.
- Preserve existing progress and schedules.
- Avoid counting speech recognition failures as learner failures.
- Keep scheduling deterministic and unit-tested.

**Deliverable:** Revision that improves actual communication rather than just quiz scores.

# **3. Supporting features**

These should run alongside the main roadmap when they unblock speaking practice.

| Feature               | Specification                                        | Priority |
| --------------------- | ---------------------------------------------------- | -------- |
| Human-recorded audio  | Record 30–50 high-frequency phrases first            | P1       |
| Phrase search         | Search English, Kannada and transliteration offline  | P1       |
| Unit learning map     | Group lessons into situations                        | P2       |
| Personal phrasebook   | Save phrases for upcoming real-life situations       | P2       |
| Content updates       | Import new curriculum without reinstalling           | P1       |
| Proficiency dashboard | Separate speaking, listening, recall and recognition | P2       |
| Contextual grammar    | Explain common spoken patterns                       | P2       |

A key curriculum recommendation: don't immediately expand the number of units. You already have Level 1 and Level 2 content. First make the existing phrases usable in spoken interactions.

# **4. Implementation sequence and dependencies**

This is the sequence I would give a coding agent.

## **Implementation dependency graph**

1. **Device audio verification**

   Confirm iOS playback, recording, interruptions and permissions.
2. **Speaking practice engine**

   Reuse the current recording and exercise infrastructure.
3. **Speech recognition abstraction**

   Add native iOS recognition and typed fallback.
4. **Answer evaluation for spoken responses**

   Normalize, compare and classify responses.
5. **Deterministic conversation engine**

   Add scenario definitions, branching and scoring.
6. **Conversation coach**

   Introduce optional AI and conversation context.
7. **Listening comprehension**

   Add audio-first dialogue exercises.
8. **Speaking-aware spaced repetition**

   Extend scheduling using the new performance dimensions.

## **Suggested development schedule**

Assuming aggressive development in a personal project, with weekly builds and device testing:

| Sprint | Primary deliverable                       |
| ------ | ----------------------------------------- |
| 1      | Audio verification + speaking exercise UX |
| 2      | Speech recognition + response evaluation  |
| 3      | Five deterministic conversation scenarios |
| 4      | AI conversation coach MVP                 |
| 5      | Listening comprehension                   |
| 6      | Speaking-aware revision                   |
| 7      | Proficiency dashboard + polish            |

These are planning estimates, not guaranteed completion dates. Device integration and speech recognition may require additional iteration.

# **5. Architecture changes**

I would preserve your current architecture rather than introduce a new backend or rewrite the application.

Your existing separation of React presentation, TypeScript domain logic, Rust/SQLite persistence and Tauri services is suitable for this roadmap.&#x20;

repomix-output(2).md



### **Proposed additions**

**Frontend —&#x20;**`src/features/`

```
speaking/
  SpeakingPracticeScreen.tsx
  SpeakingExercise.tsx
  SpeakingFeedback.tsx

conversations/
  ConversationListScreen.tsx
  ConversationPlayerScreen.tsx
  ConversationSummary.tsx

listening/
  ListeningPracticeScreen.tsx

proficiency/
  ProficiencyScreen.tsx
```

**Domain —&#x20;**`src/domain/`

```
speech/
  normalize.ts
  evaluate.ts
  feedback.ts

conversations/
  engine.ts
  evaluate-response.ts

proficiency/
  calculate.ts

revision/
  sm2.ts
```

**Services —&#x20;**`src/services/`

```
speech/
  types.ts
  index.ts
  nativeIosSpeechService.ts

conversations/
  types.ts
  engine.ts

ai/
  conversationProvider.ts

audio/
  nativeIosAudioService.ts
```

**Rust / SQLite**

```
commands/
  speech.rs
  conversations.rs
  proficiency.rs

migrations/
  004_speaking_attempts.sql
  005_conversation_sessions.sql
  006_skill_progress.sql
```

These migration names are proposed, not existing files.

### **Data model recommendations**

Don't store everything as a generic exercise attempt.

Introduce explicit concepts:

| Entity                | Important fields                             |
| --------------------- | -------------------------------------------- |
| Speaking attempt      | phrase ID, transcript, evaluation, timestamp |
| Conversation scenario | ID, difficulty, situation, content version   |
| Conversation session  | scenario ID, start/end time, completion      |
| Conversation turn     | speaker, phrase ID, response, evaluation     |
| Skill progress        | phrase ID, skill dimension, mastery state    |

Keep audio recordings separate from transcripts. Retain recordings locally only where useful, with a clear retention policy.

For AI sessions, persist recognized text and feedback only when appropriate; don't silently retain microphone recordings.

### **Testing strategy**

Continue your existing TDD discipline.

| Area                 | Tests                                                    |
| -------------------- | -------------------------------------------------------- |
| Speech normalization | Kannada script, transliteration and punctuation          |
| Response evaluation  | Accepted variants, partial responses and failures        |
| Conversation engine  | Branching, valid responses and fallback                  |
| Revision             | Different performance dimensions                         |
| Persistence          | Migrations, backup and restore                           |
| iOS integration      | Microphone permission, recording and recognition         |
| Offline              | Lessons, conversations and revision without connectivity |

Keep the domain logic testable independently of React and Tauri.

# **6. How we measure success**

I would stop treating XP and streaks as the primary indicators of learning success.

Introduce these product metrics:

| Metric                  | What it tells us                             |
| ----------------------- | -------------------------------------------- |
| Unaided speaking rate   | Can you respond without hints?               |
| Speaking success rate   | How often are responses accepted?            |
| First-attempt success   | Can you recall the phrase immediately?       |
| Listening comprehension | Can you understand spoken Kannada?           |
| Delayed recall          | Can you remember phrases after several days? |
| Conversation completion | Can you sustain an interaction?              |

**North Star Metric**

# **Successful unaided responses**

Number of distinct conversation turns successfully completed without hints or displayed answers.

This measures practical speaking ability better than the number of lessons completed.

I would initially establish a baseline, then set improvement targets after two weeks of real usage. Avoid inventing proficiency scores from XP.

# **7. What I would explicitly defer**

To protect development time:

- Full phoneme-level pronunciation scoring.
- Real-time voice-to-voice AI conversations.
- Multiple AI providers and complex model routing.
- Social features and leaderboards.
- Android development.
- Cloud synchronization.
- Dynamic curriculum generation.
- Advanced linguistic analysis.

The AI conversation coach can initially be text-mediated: listen to a recorded partner phrase, speak your response, recognize it, and receive an AI-generated next turn. That's substantially easier to validate than building a real-time voice agent.

# **8. Final prioritized backlog**

Here is the backlog I'd actually use for development.

**Development tracker**

0/14 completed

**FOUNDATION**

Verify native iOS audio and recording

P0

Build dedicated speaking practice mode

P0

**SPEECH**

Implement native speech recognition adapter

P0

Implement spoken-answer normalization and evaluation

P0

**CONVERSATION**

Build deterministic conversation engine

P0

Create five everyday conversation scenarios

P0

**INTELLIGENCE**

Implement optional AI conversation coach

P1

**LISTENING**

Build audio-first comprehension exercises

P1

**RETENTION**

Extend spaced repetition for speaking and listening

P1

**CONTENT**

Add human-recorded high-frequency audio

P1

Improve unit-based learning navigation

P2

**UX**

Add phrase search and personal phrasebook

P1

**INSIGHTS**

Build skill-specific proficiency dashboard

P2

**INFRASTRUCTURE**

Implement incremental curriculum updates

P1

&#x20;Copy backlog

## **9. My recommendation: Start with three vertical slices**

Even with aggressive development, don't ask your coding agent to implement the entire roadmap in one go.

I would begin with:

**Slice 1 — Speak and record**

Complete the physical iPhone audio workflow, speaking screen and local attempt persistence.

**Slice 2 — Speak and evaluate**

Add speech recognition, response normalization, accepted-answer evaluation and feedback.

**Slice 3 — Speak in context**

Build the deterministic conversation engine and five scenarios.

After these three slices, you'll have a meaningful speaking application even if AI integration takes longer than expected.

**One important product decision:** Kannada Quest should teach you to speak first and read Kannada script progressively. Transliteration should remain available as scaffolding, but the ultimate exercise should require you to understand and respond to spoken Kannada without looking at text.

That's the product I'd build. It has a clear purpose, measurable outcomes and a realistic architecture for a personal iOS application.