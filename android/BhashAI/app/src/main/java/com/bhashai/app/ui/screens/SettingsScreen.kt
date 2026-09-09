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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    repository: BhashAIRepository,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    var serverUrl by remember { mutableStateOf(repository.getBaseUrl()) }
    var selectedLanguage by remember { mutableStateOf("Santali (Ol Chiki)") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings", fontWeight = FontWeight.Bold) },
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
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("BACKEND SERVER CONNECTION", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                    OutlinedTextField(
                        value = serverUrl,
                        onValueChange = { serverUrl = it },
                        label = { Text("Backend Server URL") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    Button(
                        onClick = {
                            repository.updateBaseUrl(serverUrl)
                            Toast.makeText(context, "Server URL updated!", Toast.LENGTH_SHORT).show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                    ) {
                        Text("Save Server URL")
                    }
                }
            }

            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("LANGUAGE CONFIGURATION ARCHITECTURE", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                    Text("Active Target: $selectedLanguage", fontWeight = FontWeight.Bold, color = AccentTeal)

                    Text("Planned Extensible Languages:", fontSize = 12.sp, color = TextMuted)
                    Text("• Ho (hoc_Deva / Warang Citi) - Planned", fontSize = 12.sp)
                    Text("• Mundari (unr_Deva / Mundari Bani) - Planned", fontSize = 12.sp)
                }
            }
        }
    }
}
