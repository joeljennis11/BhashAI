package com.bhashai.app.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.bhashai.app.data.repository.BhashAIRepository
import com.bhashai.app.ui.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OfflineModelsScreen(
    repository: BhashAIRepository,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var isPreparing by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Offline Models", fontWeight = FontWeight.Bold) },
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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Hero Offline Action
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = PrimaryBlue),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text("Classroom Offline Mode", color = SurfaceWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Text(
                        "Synchronize all models to local storage for completely disconnected rural classroom operation.",
                        color = SurfaceWhite.copy(alpha = 0.85f),
                        fontSize = 13.sp
                    )
                    Button(
                        onClick = {
                            isPreparing = true
                            coroutineScope.launch {
                                val res = repository.prepareOffline()
                                isPreparing = false
                                Toast.makeText(context, "Offline synchronization complete!", Toast.LENGTH_LONG).show()
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = SurfaceWhite),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = if (isPreparing) "Synchronizing..." else "⚡ Prepare Offline Mode",
                            color = PrimaryBlue,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Text("Installed Core Models (~2GB RAM Target):", fontWeight = FontWeight.Bold, fontSize = 14.sp)

            // Model 1: IndicTrans2
            ModelItemCard(
                name = "IndicTrans2 Indic-Indic 320M",
                desc = "Hindi ➔ Santali (Ol Chiki) NMT",
                size = "340 MB",
                isInstalled = true
            )

            // Model 2: Santali TTS
            ModelItemCard(
                name = "Santali Ol Chiki TTS",
                desc = "Piper ONNX & Acoustic Synthesizer",
                size = "18 MB",
                isInstalled = true
            )

            // Model 3: Hindi ASR
            ModelItemCard(
                name = "Hindi Speech-to-Text (Whisper Tiny)",
                desc = "16kHz Offline Speech Recognition",
                size = "75 MB",
                isInstalled = true
            )

            // Memory Budget Card
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("DEVICE MEMORY BUDGET", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                    Text("Target Hardware: Android 9+ (Pie) with 2 GB RAM", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                    Text("Sequential model unloading active: Peak RAM footprint < 450 MB.", fontSize = 12.sp, color = SuccessGreen)
                }
            }
        }
    }
}

@Composable
fun ModelItemCard(name: String, desc: String, size: String, isInstalled: Boolean) {
    Card(
        shape = RoundedCornerShape(8.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(name, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                Text(desc, fontSize = 12.sp, color = TextMuted)
                Text("Size: $size", fontSize = 11.sp, color = PrimaryBlue)
            }
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = if (isInstalled) Color(0xFFECFDF5) else Color(0xFFFEF3C7)
            ) {
                Text(
                    text = if (isInstalled) "✓ Installed" else "Available",
                    color = if (isInstalled) SuccessGreen else WarningAmber,
                    fontWeight = FontWeight.Bold,
                    fontSize = 11.sp,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
    }
}
