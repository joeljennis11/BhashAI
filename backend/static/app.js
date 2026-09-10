/**
 * BhashAI Companion Web Application JavaScript
 * Connects frontend interface to BhashAI FastAPI backend endpoints.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabs = document.querySelectorAll(".nav-tab");
  const tabContents = document.querySelectorAll(".tab-content");
  const globalAudio = document.getElementById("global-audio-player");
  const connectionBadge = document.getElementById("connection-badge");
  const connectionText = document.getElementById("connection-text");

  // Voice Elements
  const btnMic = document.getElementById("btn-mic");
  const micText = document.getElementById("mic-text");
  const recordTimer = document.getElementById("record-timer");
  const audioFileInput = document.getElementById("audio-file-input");
  const voiceHindiOutput = document.getElementById("voice-hindi-output");
  const voiceSantaliOutput = document.getElementById("voice-santali-output");
  const voicePhoneticOutput = document.getElementById("voice-phonetic-output");
  const voicePhoneticText = document.getElementById("voice-phonetic-text");
  const btnPlayVoice = document.getElementById("btn-play-voice");
  const asrLatencyTag = document.getElementById("asr-latency");
  const transLatencyTag = document.getElementById("trans-latency");
  const totalLatencyVal = document.getElementById("total-latency");
  const latencyBreakdown = document.getElementById("latency-breakdown");
  const voiceReviewBadge = document.getElementById("voice-review-badge");
  const btnClearContext = document.getElementById("btn-clear-context");

  // Text Elements
  const textHindiInput = document.getElementById("text-hindi-input");
  const btnTranslateText = document.getElementById("btn-translate-text");
  const btnSampleText = document.getElementById("btn-sample-text");
  const textSantaliOutput = document.getElementById("text-santali-output");
  const textPhoneticOutput = document.getElementById("text-phonetic-output");
  const textPhoneticText = document.getElementById("text-phonetic-text");
  const btnPlayText = document.getElementById("btn-play-text");
  const btnCopyText = document.getElementById("btn-copy-text");
  const textLessonTopic = document.getElementById("text-lesson-topic");
  const textReviewBadge = document.getElementById("text-review-badge");

  // Worksheet Elements
  const wsTopicSelect = document.getElementById("ws-topic-select");
  const customTopicGroup = document.getElementById("custom-topic-group");
  const wsCustomTopic = document.getElementById("ws-custom-topic");
  const btnGenerateWsTopic = document.getElementById("btn-generate-ws-topic");
  const pdfDropzone = document.getElementById("pdf-dropzone");
  const pdfFileInput = document.getElementById("pdf-file-input");
  const wsBuilder = document.getElementById("worksheet-builder");
  const wsTitle = document.getElementById("ws-title");
  const wsStatusPill = document.getElementById("ws-status-pill");
  const btnApproveWs = document.getElementById("btn-approve-ws");
  const btnExportStudent = document.getElementById("btn-export-student-pdf");
  const btnExportAnswerKey = document.getElementById("btn-export-answer-key");
  const questionsList = document.getElementById("questions-list");

  // Flashcards Elements
  const cardCategoryTag = document.getElementById("card-category-tag");
  const cardHindi = document.getElementById("card-hindi");
  const cardSantali = document.getElementById("card-santali");
  const cardPhonetic = document.getElementById("card-phonetic");
  const cardExHindi = document.getElementById("card-ex-hindi");
  const cardExSantali = document.getElementById("card-ex-santali");
  const btnPlayCard = document.getElementById("btn-play-card");
  const btnPrevCard = document.getElementById("btn-prev-card");
  const btnNextCard = document.getElementById("btn-next-card");
  const currentCardIdx = document.getElementById("current-card-idx");
  const totalCardCount = document.getElementById("total-card-count");
  const categoryPills = document.querySelectorAll(".pill-btn");

  // Offline Elements
  const btnPrepareOffline = document.getElementById("btn-prepare-offline");
  const modelsGrid = document.getElementById("models-grid");
  const memoryMetrics = document.getElementById("memory-metrics");

  // State
  let currentAudioUrl = null;
  let currentPhoneticText = null;
  let isRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];
  let recordInterval = null;
  let recordSeconds = 0;
  let activeWorksheet = null;

  let allFlashcards = [];
  let flashcardsData = [];
  let activeCardIndex = 0;
  let selectedCategory = "all";

  // 1. Tab Switching
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      const targetId = `tab-${tab.dataset.tab}`;
      document.getElementById(targetId)?.classList.add("active");

      if (tab.dataset.tab === "offline") {
        fetchHealthAndModels();
      } else if (tab.dataset.tab === "flashcards" && allFlashcards.length === 0) {
        fetchDefaultFlashcards();
      }
    });
  });

  // 2. Audio Playback Helper
  function playAudio(url, fallbackPhonetic = "") {
    if (url) {
      globalAudio.src = url;
      globalAudio.play().catch(e => {
        console.warn("Server audio playback interrupted, using Web Speech fallback:", e);
        if (fallbackPhonetic && window.speechSynthesis) {
          speakWithWebSpeech(fallbackPhonetic);
        }
      });
    } else if (fallbackPhonetic && window.speechSynthesis) {
      speakWithWebSpeech(fallbackPhonetic);
    }
  }

  function speakWithWebSpeech(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = "hi-IN";
    utt.rate = 0.9;
    window.speechSynthesis.speak(utt);
  }

  // 3. Audio Recording Handling
  btnMic.addEventListener("click", async () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  });

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        await handleVoiceTranslation(audioBlob);
        stream.getTracks().forEach(t => t.stop());
      };

      mediaRecorder.start();
      isRecording = true;
      btnMic.classList.add("recording");
      micText.innerText = "STOP RECORDING";

      recordSeconds = 0;
      recordTimer.innerText = "00:00";
      recordInterval = setInterval(() => {
        recordSeconds++;
        const mins = String(Math.floor(recordSeconds / 60)).padStart(2, "0");
        const secs = String(recordSeconds % 60).padStart(2, "0");
        recordTimer.innerText = `${mins}:${secs}`;
      }, 1000);

    } catch (err) {
      console.warn("Microphone access denied or unavailable, using file upload:", err);
      audioFileInput.click();
    }
  }

  function stopRecording() {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      isRecording = false;
      btnMic.classList.remove("recording");
      micText.innerText = "START RECORDING";
      clearInterval(recordInterval);
    }
  }

  audioFileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      await handleVoiceTranslation(file);
    }
  });

  async function handleVoiceTranslation(audioSource) {
    voiceHindiOutput.innerText = "Transcribing Hindi speech...";
    voiceSantaliOutput.innerText = "Translating to Ol Chiki...";
    voicePhoneticOutput.classList.add("hidden");
    btnPlayVoice.disabled = true;
    totalLatencyVal.innerText = "Processing...";

    const formData = new FormData();
    formData.append("file", audioSource, "recording.webm");
    formData.append("source_language", "hin_Deva");
    formData.append("target_language", "sat_Olck");

    const tStartClient = performance.now();

    try {
      const resp = await fetch("/api/translate/voice", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();
      const totalClientMs = Math.round(performance.now() - tStartClient);

      if (resp.ok) {
        voiceHindiOutput.innerText = data.source_text || "(No speech recognized)";
        voiceSantaliOutput.innerText = data.translation || "(No translation)";

        const asrMs = Math.round(data.asr_latency * 1000);
        const transMs = Math.round(data.translation_latency * 1000);
        const ttsMs = Math.round(data.tts_latency * 1000);
        const totalSec = (totalClientMs / 1000).toFixed(2);

        asrLatencyTag.innerText = `${asrMs} ms`;
        transLatencyTag.innerText = `${transMs} ms`;
        totalLatencyVal.innerText = `${totalSec}s`;
        latencyBreakdown.innerText = `(ASR: ${asrMs}ms | Translation: ${transMs}ms | TTS: ${ttsMs}ms)`;

        if (totalClientMs <= 3000) {
          totalLatencyVal.style.color = "#10B981"; // Green (<3s)
        } else {
          totalLatencyVal.style.color = "#F59E0B"; // Amber
        }

        currentAudioUrl = data.audio_url;
        currentPhoneticText = data.phonetic_text || "";

        if (currentPhoneticText) {
          voicePhoneticText.innerText = currentPhoneticText;
          voicePhoneticOutput.classList.remove("hidden");
        }

        btnPlayVoice.disabled = !currentAudioUrl && !currentPhoneticText;

        if (data.review_required) {
          voiceReviewBadge.classList.remove("hidden");
        } else {
          voiceReviewBadge.classList.add("hidden");
        }

        // Auto play on voice complete
        if (currentAudioUrl || currentPhoneticText) {
          playAudio(currentAudioUrl, currentPhoneticText);
        }
      } else {
        voiceHindiOutput.innerText = `Error: ${data.detail || "Transcription failed"}`;
        voiceSantaliOutput.innerText = "";
        totalLatencyVal.innerText = "-- s";
      }
    } catch (e) {
      voiceHindiOutput.innerText = "Network error communicating with BhashAI server.";
      voiceSantaliOutput.innerText = "";
      totalLatencyVal.innerText = "-- s";
    }
  }

  btnPlayVoice.addEventListener("click", () => playAudio(currentAudioUrl, currentPhoneticText));

  btnClearContext.addEventListener("click", async () => {
    await fetch("/api/translate/clear-context", { method: "POST" });
    alert("Classroom context cleared. Starting fresh topic.");
  });

  // 4. Text Translation
  btnTranslateText.addEventListener("click", async () => {
    const text = textHindiInput.value.trim();
    if (!text) return;

    textSantaliOutput.innerText = "Translating...";
    textPhoneticOutput.classList.add("hidden");
    btnPlayText.disabled = true;

    try {
      const resp = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          source_language: "hin_Deva",
          target_language: "sat_Olck",
          lesson_topic: textLessonTopic.value.trim() || null
        })
      });
      const data = await resp.json();

      if (resp.ok) {
        textSantaliOutput.innerText = data.translation;
        currentAudioUrl = data.audio_url;
        currentPhoneticText = data.phonetic_text || "";

        if (currentPhoneticText) {
          textPhoneticText.innerText = currentPhoneticText;
          textPhoneticOutput.classList.remove("hidden");
        }

        btnPlayText.disabled = !currentAudioUrl && !currentPhoneticText;

        if (data.review_required) {
          textReviewBadge.classList.remove("hidden");
        } else {
          textReviewBadge.classList.add("hidden");
        }
      } else {
        textSantaliOutput.innerText = `Error: ${data.detail}`;
      }
    } catch (e) {
      textSantaliOutput.innerText = "Error connecting to server.";
    }
  });

  btnPlayText.addEventListener("click", () => playAudio(currentAudioUrl, currentPhoneticText));

  btnCopyText.addEventListener("click", () => {
    const text = textSantaliOutput.innerText;
    if (text) {
      navigator.clipboard.writeText(text);
      alert("Ol Chiki translation copied to clipboard!");
    }
  });

  btnSampleText.addEventListener("click", () => {
    textHindiInput.value = "आज हम फलों के बारे में सीखेंगे। यह एक आम है।";
    textLessonTopic.value = "Fruits";
  });

  // 5. Worksheet Generator & Topic Handling
  wsTopicSelect.addEventListener("change", () => {
    if (wsTopicSelect.value === "custom") {
      customTopicGroup.style.display = "flex";
    } else {
      customTopicGroup.style.display = "none";
    }
  });

  btnGenerateWsTopic.addEventListener("click", async () => {
    let chosenTopic = wsTopicSelect.value;
    let customWords = null;

    if (chosenTopic === "custom") {
      chosenTopic = wsCustomTopic.value.trim() || "बुनियादी साक्षरता (FLN)";
      customWords = wsCustomTopic.value.trim();
    }

    btnGenerateWsTopic.innerText = "Generating...";
    btnGenerateWsTopic.disabled = true;

    try {
      const resp = await fetch("/api/worksheets/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: chosenTopic,
          lesson_text: customWords,
          grade: 1,
          subject: "FLN (बुनियादी साक्षरता)",
          num_questions: 6
        })
      });
      const wsData = await resp.json();
      renderWorksheet(wsData);
    } catch (e) {
      alert("Error generating worksheet for topic.");
    } finally {
      btnGenerateWsTopic.innerText = "Generate Worksheet";
      btnGenerateWsTopic.disabled = false;
    }
  });

  pdfDropzone.addEventListener("click", () => pdfFileInput.click());

  pdfFileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      await uploadPdfAndGenerateWorksheet(file);
    }
  });

  async function uploadPdfAndGenerateWorksheet(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadResp = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData
      });
      const uploadData = await uploadResp.json();

      if (uploadResp.ok) {
        const genResp = await fetch("/api/worksheets/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lesson_id: uploadData.document_id,
            grade: uploadData.content.grade,
            subject: uploadData.content.subject,
            topic: uploadData.content.topic,
            num_questions: 6
          })
        });
        const wsData = await genResp.json();
        renderWorksheet(wsData);

        // Also populate flashcards
        fetchFlashcards(uploadData.document_id);
      } else {
        alert(`Failed to parse PDF: ${uploadData.detail}`);
      }
    } catch (e) {
      alert("Error uploading PDF.");
    }
  }

  function renderWorksheet(ws) {
    activeWorksheet = ws;
    wsBuilder.classList.remove("hidden");
    wsTitle.value = ws.title;
    wsStatusPill.innerText = ws.status;
    wsStatusPill.className = `pill pill-${ws.status.toLowerCase()}`;

    questionsList.innerHTML = "";
    ws.questions.forEach((q) => {
      const item = document.createElement("div");
      item.className = "question-item";

      let optionsHtml = "";
      if (q.options_hindi || q.options_santali) {
        const optsH = q.options_hindi || [];
        const optsS = q.options_santali || [];
        const maxLen = Math.max(optsH.length, optsS.length);
        optionsHtml = `<div class="q-options-row" style="display: flex; gap: 14px; margin-top: 6px; font-size: 13px;">`;
        for (let i = 0; i < maxLen; i++) {
          const lbl = String.fromCharCode(65 + i);
          const h = optsH[i] || "";
          const s = optsS[i] ? ` (<span class="font-olchiki">${optsS[i]}</span>)` : "";
          optionsHtml += `<span>(${lbl}) ${h}${s}</span>`;
        }
        optionsHtml += `</div>`;
      }

      item.innerHTML = `
        <div class="q-header">
          <span>Question ${q.id} [${q.question_type}]</span>
          <span>Source: ${q.source_reference || "Curriculum"}</span>
        </div>
        <div class="q-prompt-hindi">${q.hindi_prompt}</div>
        <div class="q-prompt-santali font-olchiki">${q.santali_prompt}</div>
        ${optionsHtml}
        <div class="q-answer-row">
          <strong>Answer:</strong>
          <span>${q.answer_hindi} / <span class="font-olchiki">${q.answer_santali}</span></span>
          ${q.audio_url ? `<button class="btn btn-sm btn-ghost" onclick="playQuestionAudio('${q.audio_url}', '${q.phonetic_answer || ''}')">Play</button>` : ""}
        </div>
      `;
      questionsList.appendChild(item);
    });
  }

  window.playQuestionAudio = (url, phonetic) => playAudio(url, phonetic);

  btnApproveWs.addEventListener("click", async () => {
    if (!activeWorksheet) return;
    try {
      const resp = await fetch(`/api/worksheets/${activeWorksheet.worksheet_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: wsTitle.value,
          status: "APPROVED"
        })
      });
      const updated = await resp.json();
      activeWorksheet = updated;
      wsStatusPill.innerText = "APPROVED";
      wsStatusPill.className = "pill pill-approved";
      alert("Worksheet approved! You can now export the classroom PDF.");
    } catch (e) {
      alert("Failed to update worksheet status.");
    }
  });

  btnExportStudent.addEventListener("click", () => {
    if (!activeWorksheet) return;
    window.open(`/api/worksheets/${activeWorksheet.worksheet_id}/export?type=student&mode=bilingual`, "_blank");
  });

  btnExportAnswerKey.addEventListener("click", () => {
    if (!activeWorksheet) return;
    window.open(`/api/worksheets/${activeWorksheet.worksheet_id}/export?type=answer_key&mode=bilingual`, "_blank");
  });

  // 6. Flashcards Carousel Navigation & Dynamic Loading
  async function fetchDefaultFlashcards() {
    try {
      const resp = await fetch("/api/flashcards/default");
      const data = await resp.json();
      if (resp.ok && data.cards && data.cards.length > 0) {
        allFlashcards = data.cards.map(c => ({
          hindi: c.hindi_word,
          santali: c.santali_word,
          phonetic: `${c.phonetic || ''} (${c.concept})`,
          category: c.icon || "Vocab",
          ex_hi: c.example_hindi,
          ex_sat: c.example_santali,
          audio_url: c.audio_url
        }));
        filterFlashcardsByCategory(selectedCategory);
      }
    } catch (e) {
      console.warn("Failed to fetch default flashcards, using offline fallback:", e);
      initFallbackFlashcards();
    }
  }

  async function fetchFlashcards(docId) {
    try {
      const resp = await fetch(`/api/flashcards/lesson/${docId}`);
      const data = await resp.json();
      if (resp.ok && data.cards && data.cards.length > 0) {
        allFlashcards = data.cards.map(c => ({
          hindi: c.hindi_word,
          santali: c.santali_word,
          phonetic: `${c.phonetic || ''} (${c.concept})`,
          category: c.icon || "Lesson",
          ex_hi: c.example_hindi,
          ex_sat: c.example_santali,
          audio_url: c.audio_url
        }));
        filterFlashcardsByCategory("all");
      }
    } catch (e) {
      console.warn("Failed to fetch lesson flashcards:", e);
    }
  }

  function initFallbackFlashcards() {
    allFlashcards = [
      { hindi: "आम", santali: "ᱩᱞ", phonetic: "Ul (Mango)", category: "Fruits", ex_hi: "यह एक आम है।", ex_sat: "ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾", audio_url: null },
      { hindi: "सेब", santali: "ᱥᱮᱣ", phonetic: "Sew (Apple)", category: "Fruits", ex_hi: "सेब लाल होता है।", ex_sat: "ᱥᱮᱣ ᱫᱚ ᱟᱨᱟᱜ ᱜᱮᱭᱟ ᱾", audio_url: null },
      { hindi: "केला", santali: "ᱠᱟᱭᱨᱟ", phonetic: "Kayra (Banana)", category: "Fruits", ex_hi: "केला मीठा होता है।", ex_sat: "ᱠᱟᱭᱨᱟ ᱫᱚ ᱦᱮᱲᱮᱢ ᱜᱮᱭᱟ ᱾", audio_url: null },
      { hindi: "एक", santali: "ᱢᱤᱫ", phonetic: "Mid (One)", category: "Numbers", ex_hi: "टोकरी में एक फल है।", ex_sat: "ᱴᱩᱠᱨᱤ ᱨᱮ ᱢᱤᱫ ᱡᱚ ᱢᱮᱱᱟᱜ-ᱟ ᱾", audio_url: null },
      { hindi: "दो", santali: "ᱵᱟᱨ", phonetic: "Bar (Two)", category: "Numbers", ex_hi: "दो बच्चे पढ़ रहे हैं।", ex_sat: "ᱵᱟᱨ ᱜᱤᱫᱽᱨᱟᱹ ᱠᱤᱱ ᱯᱟᱲᱦᱟᱣᱜ ᱠᱟᱱᱟ ᱾", audio_url: null },
      { hindi: "पेड़", santali: "ᱫᱟᱨᱮ", phonetic: "Dare (Tree)", category: "Nature", ex_hi: "पेड़ पर हरे पत्ते हैं।", ex_sat: "ᱫᱟᱨᱮ ᱨᱮ ᱦᱟᱹᱨᱭᱟᱹᱲ ᱥᱟᱠᱟᱢ ᱢᱮᱱᱟᱜ-ᱟ ᱾", audio_url: null },
      { hindi: "किताब", santali: "ᱯᱩᱛᱷᱤ", phonetic: "Puthi (Book)", category: "Classroom", ex_hi: "अपनी किताब खोलिए।", ex_sat: "ᱟᱢᱟᱜ ᱯᱩᱛᱷᱤ ᱡᱷᱤᱡᱽ ᱢᱮ ᱾", audio_url: null },
      { hindi: "नमस्ते", santali: "ᱡᱚᱦᱟᱨ", phonetic: "Johar (Greetings)", category: "Phrases", ex_hi: "नमस्ते, आप सब कैसे हैं?", ex_sat: "ᱡᱚᱦᱟᱨ, ᱟᱯᱮ ᱪᱮᱫ ᱞᱮᱠᱟ ᱢᱮᱱᱟᱜ ᱯᱮᱭᱟ?", audio_url: null }
    ];
    filterFlashcardsByCategory("all");
  }

  function filterFlashcardsByCategory(category) {
    selectedCategory = category;
    if (category === "all") {
      flashcardsData = [...allFlashcards];
    } else {
      flashcardsData = allFlashcards.filter(c => c.category.toLowerCase() === category.toLowerCase());
    }
    activeCardIndex = 0;
    updateFlashcardDisplay();
  }

  categoryPills.forEach(pill => {
    pill.addEventListener("click", () => {
      categoryPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      filterFlashcardsByCategory(pill.dataset.category);
    });
  });

  function updateFlashcardDisplay() {
    if (!flashcardsData || flashcardsData.length === 0) return;
    const card = flashcardsData[activeCardIndex];
    cardCategoryTag.innerText = card.category || "Vocabulary";
    cardHindi.innerText = card.hindi;
    cardSantali.innerText = card.santali;
    cardPhonetic.innerText = card.phonetic || "";
    cardExHindi.innerText = card.ex_hi || "";
    cardExSantali.innerText = card.ex_sat || "";
    currentCardIdx.innerText = activeCardIndex + 1;
    totalCardCount.innerText = flashcardsData.length;
  }

  btnPrevCard.addEventListener("click", () => {
    if (flashcardsData.length > 0) {
      activeCardIndex = (activeCardIndex - 1 + flashcardsData.length) % flashcardsData.length;
      updateFlashcardDisplay();
    }
  });

  btnNextCard.addEventListener("click", () => {
    if (flashcardsData.length > 0) {
      activeCardIndex = (activeCardIndex + 1) % flashcardsData.length;
      updateFlashcardDisplay();
    }
  });

  btnPlayCard.addEventListener("click", async () => {
    const card = flashcardsData[activeCardIndex];
    if (!card) return;
    if (card.audio_url) {
      playAudio(card.audio_url, card.phonetic);
    } else {
      // Synthesize on demand
      btnPlayCard.innerText = "Synthesizing...";
      btnPlayCard.disabled = true;
      try {
        const resp = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: card.santali })
        });
        const data = await resp.json();
        if (data.audio_url) {
          card.audio_url = data.audio_url;
          playAudio(data.audio_url, data.phonetic_text);
        }
      } catch (e) {
        console.warn("Audio synthesis error:", e);
      } finally {
        btnPlayCard.innerText = "Listen Pronunciation";
        btnPlayCard.disabled = false;
      }
    }
  });

  // 7. Offline Models & Diagnostics
  async function fetchHealthAndModels() {
    try {
      const resp = await fetch("/api/health");
      const data = await resp.json();

      if (data.offline_mode) {
        connectionBadge.className = "badge-status badge-offline";
        connectionText.innerText = "OFFLINE READY";
      } else {
        connectionBadge.className = "badge-status badge-online";
        connectionText.innerText = "ONLINE";
      }

      // Render Models Grid
      modelsGrid.innerHTML = "";
      Object.values(data.models).forEach(m => {
        const item = document.createElement("div");
        item.className = "model-card";
        item.innerHTML = `
          <div class="model-card-header">
            <span>${m.name}</span>
            <span class="pill ${m.installed ? "pill-approved" : "pill-draft"}">
              ${m.installed ? "Installed" : "Not Installed"}
            </span>
          </div>
          <p style="font-size: 13px; color: #64748B;">Size: ${m.size_mb} MB | Status: ${m.in_memory ? "In RAM" : "Standby"}</p>
        `;
        modelsGrid.appendChild(item);
      });

      // Render Memory Metrics
      memoryMetrics.innerHTML = `
        <div class="metric-item">Process RSS: <strong>${data.memory.process_rss_mb} MB</strong></div>
        <div class="metric-item">Available RAM: <strong>${data.memory.available_ram_mb} MB</strong></div>
        <div class="metric-item">RAM Usage: <strong>${data.memory.ram_percent}%</strong></div>
        <div class="metric-item">Target Device: <strong>Android 9+ (2GB)</strong></div>
      `;
    } catch (e) {
      connectionBadge.className = "badge-status badge-offline";
      connectionText.innerText = "OFFLINE";
    }
  }

  btnPrepareOffline.addEventListener("click", async () => {
    btnPrepareOffline.innerText = "Synchronizing Models...";
    btnPrepareOffline.disabled = true;
    try {
      const resp = await fetch("/api/models/prepare-offline", { method: "POST" });
      const data = await resp.json();
      alert(`Offline Preparation Complete: ${data.status} in ${data.preparation_time_seconds}s!`);
      fetchHealthAndModels();
    } catch (e) {
      alert("Offline preparation failed. Check console.");
    } finally {
      btnPrepareOffline.innerText = "Prepare Offline Mode";
      btnPrepareOffline.disabled = false;
    }
  });

  // Initial Startup Actions
  fetchHealthAndModels();
  fetchDefaultFlashcards();
});

