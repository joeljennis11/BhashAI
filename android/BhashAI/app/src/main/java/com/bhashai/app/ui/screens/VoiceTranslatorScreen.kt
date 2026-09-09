package com.bhashai.app.ui.screens

import android.media.MediaPlayer
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.bhashai.app.data.repository.BhashAIRepository
import com.bhashai.app.ui.theme.*
import kotlinx.coroutines.launch
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceTranslatorScreen(
    repository: BhashAIRepository,
    onBack: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()

    var isRecording by remember { mutableStateOf(false) }
    var hindiText by remember { mutableStateOf("") }
    var santaliText by remember { mutableStateOf("") }
    var audioUrl by remember { mutableStateOf<String?>(null) }
    var reviewRequired by remember { mutableStateOf(false) }
    var isContextOn by remember { mutableStateOf(true) }
    var isLoading by remember { mutableStateOf(false) }
    var latencyInfo by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Voice Translator", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceWhite)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(BackgroundLight)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Direction Card
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Hindi (हिन्दी)", fontWeight = FontWeight.Bold, color = TextDark)
                    Icon(Icons.Default.ArrowForward, contentDescription = null, tint = PrimaryBlue)
                    Text("Santali (ᱚᱞ ᱪᱤᱠᱤ)", fontWeight = FontWeight.Bold, color = AccentTeal)
                }
            }

            // Context Bar
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(SurfaceWhite, RoundedCornerShape(8.dp))
                    .padding(horizontal = 14.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Switch(
                        checked = isContextOn,
                        onCheckedChange = { isContextOn = it }
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Context: ${if (isContextOn) "ON" else "OFF"}",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                TextButton(
                    onClick = {
                        hindiText = ""
                        santaliText = ""
                        audioUrl = null
                        reviewRequired = false
                    }
                ) {
                    Text("Clear Context", fontSize = 12.sp, color = TextMuted)
                }
            }

            // Recording Button
            Box(
                modifier = Modifier.padding(vertical = 16.dp),
                contentAlignment = Alignment.Center
            ) {
                Button(
                    onClick = {
                        if (!isRecording) {
                            isRecording = true
                            isLoading = true
                            // Simulate microphone recording and call repository
                            coroutineScope.launch {
                                // Simulate audio recording turnaround
                                val demoFile = File.createTempFile("voice_", ".wav")
                                val result = repository.translateVoice(demoFile, topic = if (isContextOn) "Fruits" else null)
                                result.onSuccess { data ->
                                    hindiText = data.sourceText
                                    santaliText = data.translation
                                    audioUrl = data.audioUrl
                                    reviewRequired = data.reviewRequired
                                    latencyInfo = "Latency: ${(data.totalLatency * 1000).toInt()} ms"
                                }
                                isRecording = false
                                isLoading = false
                            }
                        } else {
                            isRecording = false
                        }
                    },
                    shape = CircleShape,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isRecording) Color(0xFFEF4444) else PrimaryBlue
                    ),
                    modifier = Modifier.size(110.dp)
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(if (isRecording) "⏹️" else "🎙️", fontSize = 32.sp)
                        Text(
                            text = if (isRecording) "RECORDING" else "SPEAK",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            if (isLoading) {
                CircularProgressIndicator(color = PrimaryBlue)
                Text("Processing Hindi Speech...", fontSize = 13.sp, color = TextMuted)
            }

            // Output 1: Spoken Hindi
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("HINDI ASR RESULT", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = hindiText.ifEmpty { "Teacher's spoken Hindi will appear here..." },
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (hindiText.isEmpty()) TextMuted else TextDark
                    )
                }
            }

            // Output 2: Santali Ol Chiki Translation
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("SANTALI (OL CHIKI)", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = AccentTeal)
                        if (reviewRequired) {
                            Text(
                                text = "⚠️ Review recommended",
                                fontSize = 11.sp,
                                color = WarningAmber,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = santaliText.ifEmpty { "Santali Ol Chiki translation will appear here..." },
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (santaliText.isEmpty()) TextMuted else AccentTeal
                    )

                    Spacer(modifier = Modifier.height(14.dp))
                    Button(
                        onClick = {
                            // Play audio via MediaPlayer
                            if (audioUrl != null) {
                                try {
                                    val fullUrl = if (audioUrl!!.startsWith("http")) audioUrl!! else "${repository.getBaseUrl().trimEnd('/')}${audioUrl}"
                                    val player = MediaPlayer()
                                    player.setDataSource(fullUrl)
                                    player.prepareAsync()
                                    player.setOnPreparedListener { it.start() }
                                } catch (e: Exception) {
                                    // Audio playback handled
                                }
                            }
                        },
                        enabled = santaliText.isNotEmpty(),
                        colors = ButtonDefaults.buttonColors(containerColor = AccentTeal),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("🔊 Play Santali Audio", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    }
                }
            }

            if (latencyInfo.isNotEmpty()) {
                Text(latencyInfo, fontSize = 12.sp, color = TextMuted)
            }
        }
    }
}
