package com.bhashai.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.bhashai.app.ui.theme.*

data class HomeMenuItem(
    val title: String,
    val subtitle: String,
    val icon: String,
    val route: String,
    val color: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    isOffline: Boolean = false,
    onNavigate: (String) -> Unit
) {
    val menuItems = listOf(
        HomeMenuItem("Voice Translation", "Speak Hindi, hear Santali", "🎤", "voice", PrimaryBlue),
        HomeMenuItem("Text Translation", "Translate sentences & lessons", "📝", "text", AccentTeal),
        HomeMenuItem("Lesson Materials", "Upload & view curriculum", "📚", "lessons", Color(0xFF8B5CF6)),
        HomeMenuItem("Generate Worksheet", "Printable bilingual A4 PDFs", "📄", "worksheets", Color(0xFFF59E0B)),
        HomeMenuItem("Flashcards", "Visual vocabulary drill", "🖼️", "flashcards", Color(0xFFEC4899)),
        HomeMenuItem("Offline Resources", "Model management & RAM", "📴", "offline", Color(0xFF10B981)),
        HomeMenuItem("Settings", "Server URL & languages", "⚙️", "settings", Color(0xFF64748B)),
        HomeMenuItem("About BhashAI", "SIH project information", "ℹ️", "about", Color(0xFF0284C7))
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("BHASH AI", fontWeight = FontWeight.Bold, fontSize = 20.sp, color = PrimaryBlue)
                        Text("AI-assisted vernacular education", fontSize = 12.sp, color = TextMuted)
                    }
                },
                actions = {
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = if (isOffline) Color(0xFFFEF3C7) else Color(0xFFECFDF5),
                        modifier = Modifier.padding(end = 12.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(if (isOffline) WarningAmber else SuccessGreen)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = if (isOffline) "OFFLINE" else "ONLINE",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (isOffline) Color(0xFFB45309) else Color(0xFF059669)
                            )
                        }
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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Language Pair Card
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = PrimaryLight),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Language Pair", fontSize = 12.sp, color = PrimaryDark, fontWeight = FontWeight.Medium)
                        Text("हिन्दी (Hindi)  ➔  ᱥᱟᱱᱛᱟᱲᱤ (Santali)", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = PrimaryDark)
                    }
                    Text("Ol Chiki", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = AccentTeal)
                }
            }

            // Grid of Options
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                items(menuItems.size) { idx ->
                    val item = menuItems[idx]
                    Card(
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                        elevation = CardDefaults.cardElevation(2.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(130.dp)
                            .clickable { onNavigate(item.route) }
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(14.dp),
                            verticalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(item.icon, fontSize = 28.sp)
                            Column {
                                Text(item.title, fontWeight = FontWeight.Bold, fontSize = 14.sp, color = TextDark)
                                Text(item.subtitle, fontSize = 11.sp, color = TextMuted, maxLines = 1)
                            }
                        }
                    }
                }
            }
        }
    }
}
