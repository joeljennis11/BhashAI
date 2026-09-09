# BhashAI Android Application Architecture

## Target Specifications

- **Operating System:** Android 9.0+ (API level 28+)
- **Target Architecture:** ARM64 / ARMv7 CPU-only devices
- **RAM Target:** ~2 GB RAM entry-level smartphones
- **UI Framework:** Jetpack Compose with Material Design 3
- **Language:** Kotlin
- **Architecture:** Clean Architecture / MVVM

---

## Screen Navigation Structure

```
              ┌──────────────┐
              │ SplashScreen │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │  HomeScreen  │
              └──────┬───────┘
                     │
       ┌─────────────┼─────────────┬─────────────┐
       │             │             │             │
┌──────▼──────┐┌─────▼──────┐┌─────▼──────┐┌─────▼──────┐
│VoiceTranslate│TextTranslate│  Worksheet  │ Flashcards  │
└─────────────┘└────────────┘└────────────┘└────────────┘
       │             │             │             │
┌──────▼──────┐┌─────▼──────┐┌─────▼──────┐┌─────▼──────┐
│LessonMaterial│OfflineModel │  Settings   │    About    │
└─────────────┘└────────────┘└────────────┘└────────────┘
```

---

## 10 Production Screens

1. **Splash Screen:** Application branding and offline readiness verification.
2. **Home Screen:** Fast action tiles for teachers, Online/Offline badge, language pair banner.
3. **Voice Translator:** Hold-to-speak recording, live Hindi ASR output, Ol Chiki translation, 🔊 Play Santali audio, Context toggle with topic indicator.
4. **Text Translator:** Text input, translation, copy to clipboard, 🔊 Play audio.
5. **Lesson Materials:** View uploaded PDFs, extracted curriculum topics, page numbers.
6. **Worksheet Generator:** Configure grade, subject, question format, preview questions, edit prompts, approve status, export PDF.
7. **Flashcards:** Visual card carousel (icon, Hindi word, Santali Ol Chiki word, example, 🔊 Play button).
8. **Offline Models:** Model status monitor (Installed/Standby), file sizes, "Prepare Offline Mode" trigger.
9. **Settings:** Backend server IP/URL configuration, language selection, cache settings.
10. **About:** Project mission, FLN context, SIH details.

---

## Building and Running Android App

Open the `android/BhashAI` project in Android Studio or build using Gradle wrapper:

```powershell
cd android/BhashAI
./gradlew assembleDebug
```
