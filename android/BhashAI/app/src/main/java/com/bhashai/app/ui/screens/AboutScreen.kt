package com.bhashai.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.bhashai.app.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AboutScreen(onBack: () -> Unit) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("About BhashAI", fontWeight = FontWeight.Bold) },
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
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("BHASH AI", fontSize = 22.sp, fontWeight = FontWeight.ExtraBold, color = PrimaryBlue)
                    Text("AI-assisted vernacular education and classroom communication application designed for teachers teaching foundational literacy and numeracy (FLN) content to children speaking Indian tribal/vernacular languages.", fontSize = 14.sp, color = TextDark)
                    Divider(color = BorderColor)
                    Text("Architecture Specifications:", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                    Text("• Target Platform: Android 9+ (API 28+)", fontSize = 12.sp)
                    Text("• Target RAM: ~2 GB low-cost smartphones", fontSize = 12.sp)
                    Text("• ASR Model: Whisper 16kHz Hindi ASR", fontSize = 12.sp)
                    Text("• Translation Model: IndicTrans2 320M (hin_Deva ➔ sat_Olck)", fontSize = 12.sp)
                    Text("• TTS Model: Piper-compatible Santali Ol Chiki Voice", fontSize = 12.sp)
                    Text("• Offline Capability: Full local cached inference", fontSize = 12.sp)
                }
            }
        }
    }
}
