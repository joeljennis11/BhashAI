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
  const btnPlayVoice = document.getElementById("btn-play-voice");
  const asrLatencyTag = document.getElementById("asr-latency");
  const transLatencyTag = document.getElementById("trans-latency");
  const voiceReviewBadge = document.getElementById("voice-review-badge");
  const btnClearContext = document.getElementById("btn-clear-context");

  // Text Elements
  const textHindiInput = document.getElementById("text-hindi-input");
  const btnTranslateText = document.getElementById("btn-translate-text");
  const btnSampleText = document.getElementById("btn-sample-text");
  const textSantaliOutput = document.getElementById("text-santali-output");
  const btnPlayText = document.getElementById("btn-play-text");
  const btnCopyText = document.getElementById("btn-copy-text");
  const textLessonTopic = document.getElementById("text-lesson-topic");
  const textReviewBadge = document.getElementById("text-review-badge");

  // Worksheet Elements
  const pdfDropzone = document.getElementById("pdf-dropzone");
  const pdfFileInput = document.getElementById("pdf-file-input");
  const btnSamplePdf = document.getElementById("btn-sample-pdf");
  const wsBuilder = document.getElementById("worksheet-builder");
  const wsTitle = document.getElementById("ws-title");
  const wsStatusPill = document.getElementById("ws-status-pill");
  const btnApproveWs = document.getElementById("btn-approve-ws");
  const btnExportStudent = document.getElementById("btn-export-student-pdf");
  const btnExportAnswerKey = document.getElementById("btn-export-answer-key");
  const questionsList = document.getElementById("questions-list");

  // Flashcards Elements
  const cardActive = document.getElementById("flashcard-active");
  const cardIcon = document.getElementById("card-icon");
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

  // Offline Elements
  const btnPrepareOffline = document.getElementById("btn-prepare-offline");
  const modelsGrid = document.getElementById("models-grid");
  const memoryMetrics = document.getElementById("memory-metrics");

  // State
  let currentAudioUrl = null;
  let isRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];
  let recordInterval = null;
  let recordSeconds = 0;
  let activeWorksheet = null;
  let flashcardsData = [];
  let activeCardIndex = 0;

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
      }
    });
  });

  // 2. Audio Playback Helper
  function playAudio(url) {
    if (!url) return;
    globalAudio.src = url;
    globalAudio.play().catch(e => console.warn("Audio playback interrupted:", e));
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
    btnPlayVoice.disabled = true;

    const formData = new FormData();
    formData.append("file", audioSource, "recording.webm");
    formData.append("source_language", "hin_Deva");
    formData.append("target_language", "sat_Olck");

    try {
      const resp = await fetch("/api/translate/voice", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();

      if (resp.ok) {
        voiceHindiOutput.innerText = data.source_text || "(No speech recognized)";
        voiceSantaliOutput.innerText = data.translation || "(No translation)";
        asrLatencyTag.innerText = `${Math.round(data.asr_latency * 1000)} ms`;
        transLatencyTag.innerText = `${Math.round(data.translation_latency * 1000)} ms`;

        currentAudioUrl = data.audio_url;
        btnPlayVoice.disabled = !currentAudioUrl;

        if (data.review_required) {
          voiceReviewBadge.classList.remove("hidden");
        } else {
          voiceReviewBadge.classList.add("hidden");
        }

        // Auto play on voice complete
        if (currentAudioUrl) {
          playAudio(currentAudioUrl);
        }
      } else {
        voiceHindiOutput.innerText = `Error: ${data.detail || "Transcription failed"}`;
        voiceSantaliOutput.innerText = "";
      }
    } catch (e) {
      voiceHindiOutput.innerText = "Network error communicating with BhashAI server.";
      voiceSantaliOutput.innerText = "";
    }
  }

  btnPlayVoice.addEventListener("click", () => playAudio(currentAudioUrl));

  btnClearContext.addEventListener("click", async () => {
    await fetch("/api/translate/clear-context", { method: "POST" });
    alert("Classroom context cleared. Starting fresh topic.");
  });

  // 4. Text Translation
  btnTranslateText.addEventListener("click", async () => {
    const text = textHindiInput.value.trim();
    if (!text) return;

    textSantaliOutput.innerText = "Translating...";
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
        btnPlayText.disabled = !currentAudioUrl;

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

  btnPlayText.addEventListener("click", () => playAudio(currentAudioUrl));

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

  // 5. Worksheet Generator & PDF Handling
  pdfDropzone.addEventListener("click", () => pdfFileInput.click());

  pdfFileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      await uploadPdfAndGenerateWorksheet(file);
    }
  });

  btnSamplePdf.addEventListener("click", async (e) => {
    e.stopPropagation();
    // Generate synthetic lesson directly for demo
    await generateWorksheetFromDemo();
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
        // Generate worksheet from document ID
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

  async function generateWorksheetFromDemo() {
    try {
      const resp = await fetch("/api/worksheets/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_text: "आम सेब केला संतरा अंगूर अमरूद",
          grade: 1,
          subject: "FLN (बुनियादी साक्षरता)",
          topic: "फलों के नाम (Fruits)",
          num_questions: 6
        })
      });
      const wsData = await resp.json();
      renderWorksheet(wsData);

      // Populate demo flashcards
      flashcardsData = [
        { hindi: "आम", santali: "ᱩᱞ", phonetic: "Ul (Mango)", icon: "🥭", ex_hi: "यह एक आम है।", ex_sat: "ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾" },
        { hindi: "सेब", santali: "ᱥᱮᱣ", phonetic: "Sew (Apple)", icon: "🍎", ex_hi: "सेब लाल होता है।", ex_sat: "ᱥᱮᱣ ᱫᱚ ᱟᱨᱟᱜ ᱜᱮᱭᱟ ᱾" },
        { hindi: "केला", santali: "ᱠᱟᱭᱨᱟ", phonetic: "Kayra (Banana)", icon: "🍌", ex_hi: "केला मीठा होता है।", ex_sat: "ᱠᱟᱭᱨᱟ ᱫᱚ ᱦᱮᱲᱮᱢ ᱜᱮᱭᱟ ᱾" },
        { hindi: "अंगूर", santali: "ᱟᱝᱜᱩᱨ", phonetic: "Angur (Grapes)", icon: "🍇", ex_hi: "अंगूर गुच्छों में होते हैं।", ex_sat: "ᱟᱝᱜᱩᱨ ᱫᱚ ᱜᱩᱪᱷᱟᱹ ᱨᱮ ᱛᱟᱦᱮᱸᱱᱟ ᱾" }
      ];
      activeCardIndex = 0;
      updateFlashcardDisplay();
    } catch (e) {
      alert("Error generating demo worksheet.");
    }
  }

  function renderWorksheet(ws) {
    activeWorksheet = ws;
    wsBuilder.classList.remove("hidden");
    wsTitle.value = ws.title;
    wsStatusPill.innerText = ws.status;
    wsStatusPill.className = `pill pill-${ws.status.toLowerCase()}`;

    questionsList.innerHTML = "";
    ws.questions.forEach((q, idx) => {
      const item = document.createElement("div");
      item.className = "question-item";
      item.innerHTML = `
        <div class="q-header">
          <span>Question ${q.id} (${q.question_type})</span>
          <span>Source: ${q.source_reference || "Curriculum"}</span>
        </div>
        <div class="q-prompt-hindi">${q.hindi_prompt}</div>
        <div class="q-prompt-santali font-olchiki">${q.santali_prompt}</div>
        <div class="q-answer-row">
          <strong>Answer:</strong>
          <span>${q.answer_hindi} / <span class="font-olchiki">${q.answer_santali}</span></span>
          ${q.audio_url ? `<button class="btn btn-sm btn-ghost" onclick="playQuestionAudio('${q.audio_url}')">🔊 Play</button>` : ""}
        </div>
      `;
      questionsList.appendChild(item);
    });
  }

  window.playQuestionAudio = (url) => playAudio(url);

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

  // 6. Flashcards Carousel
  async function fetchFlashcards(docId) {
    try {
      const resp = await fetch(`/api/flashcards/lesson/${docId}`);
      const data = await resp.json();
      if (resp.ok && data.cards && data.cards.length > 0) {
        flashcardsData = data.cards.map(c => ({
          hindi: c.hindi_word,
          santali: c.santali_word,
          phonetic: `${c.concept}`,
          icon: c.icon,
          ex_hi: c.example_hindi,
          ex_sat: c.example_santali,
          audio_url: c.audio_url
        }));
        activeCardIndex = 0;
        updateFlashcardDisplay();
      }
    } catch (e) {
      console.warn("Failed to fetch flashcards:", e);
    }
  }

  function updateFlashcardDisplay() {
    if (!flashcardsData || flashcardsData.length === 0) return;
    const card = flashcardsData[activeCardIndex];
    cardIcon.innerText = card.icon || "🥭";
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
      playAudio(card.audio_url);
    } else {
      // Synthesize on demand
      try {
        const resp = await fetch("/api/tts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: card.santali })
        });
        const data = await resp.json();
        if (data.audio_url) {
          card.audio_url = data.audio_url;
          playAudio(data.audio_url);
        }
      } catch (e) {
        console.warn("Audio synthesis error:", e);
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
              ${m.installed ? "✓ Installed" : "Not Installed"}
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
      btnPrepareOffline.innerText = "⚡ Prepare Offline Mode";
      btnPrepareOffline.disabled = false;
    }
  });

  // Initial Check
  fetchHealthAndModels();
});
