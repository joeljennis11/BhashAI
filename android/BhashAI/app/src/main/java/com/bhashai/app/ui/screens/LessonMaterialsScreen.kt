package com.bhashai.app.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
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
fun LessonMaterialsScreen(
    repository: BhashAIRepository,
    onBack: () -> Unit,
    onOpenWorksheet: () -> Unit
) {
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Lesson Materials", fontWeight = FontWeight.Bold) },
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
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Button(
                onClick = {
                    Toast.makeText(context, "Select PDF from device storage...", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
            ) {
                Text("📤 Upload Educational PDF", fontWeight = FontWeight.Bold)
            }

            Text("Classroom Curriculum Lessons:", fontWeight = FontWeight.Bold, fontSize = 14.sp)

            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                item {
                    Card(
                        shape = RoundedCornerShape(10.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onOpenWorksheet() }
                    ) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text("Class 1: Fruits (फल)", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                                Text("FLN Literacy", fontSize = 12.sp, color = PrimaryDark)
                            }
                            Text("Extracted Vocabulary: आम, सेब, केला, अंगूर, संतरा", fontSize = 13.sp, color = TextMuted)
                            Text("Source: class1_fruits_hindi.pdf • 1 Page", fontSize = 11.sp, color = AccentTeal)
                        }
                    }
                }
            }
        }
    }
}
