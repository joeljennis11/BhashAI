package com.bhashai.app.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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
import com.bhashai.app.data.model.FlashcardItemDto
import com.bhashai.app.data.repository.BhashAIRepository
import com.bhashai.app.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FlashcardsScreen(
    repository: BhashAIRepository,
    onBack: () -> Unit
) {
    val context = LocalContext.current

    val cards = remember {
        listOf(
            FlashcardItemDto(1, "आम", "ᱩᱞ", "Ul", "Mango", "🥭", "यह एक आम है।", "ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾", null),
            FlashcardItemDto(2, "सेब", "ᱥᱮᱣ", "Sew", "Apple", "🍎", "सेब लाल होता है।", "ᱥᱮᱣ ᱫᱚ ᱟᱨᱟᱜ ᱜᱮᱭᱟ ᱾", null),
            FlashcardItemDto(3, "केला", "ᱠᱟᱭᱨᱟ", "Kayra", "Banana", "🍌", "केला मीठा होता है।", "ᱠᱟᱭᱨᱟ ᱫᱚ ᱦᱮᱲᱮᱢ ᱜᱮᱭᱟ ᱾", null),
            FlashcardItemDto(4, "अंगूर", "ᱟᱝᱜᱩᱨ", "Angur", "Grapes", "🍇", "अंगूर खट्टे-मीठे होते हैं।", "ᱟᱝᱜᱩᱨ ᱫᱚ ᱦᱮᱲᱮᱢ-ᱡᱚᱡᱚ ᱜᱮᱭᱟ ᱾", null)
        )
    }

    var currentIndex by remember { mutableStateOf(0) }
    val currentCard = cards[currentIndex]

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Visual Flashcards", fontWeight = FontWeight.Bold) },
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
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Topic: Fruits (Class 1 FLN)", fontWeight = FontWeight.Bold, color = TextMuted)

            // Flashcard
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = SurfaceWhite),
                elevation = CardDefaults.cardElevation(4.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(380.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(currentCard.icon, fontSize = 72.sp)

                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(currentCard.hindiWord, fontSize = 24.sp, fontWeight = FontWeight.Bold, color = TextDark)
                        Text(currentCard.santaliWord, fontSize = 36.sp, fontWeight = FontWeight.ExtraBold, color = AccentTeal)
                        if (currentCard.phonetic != null) {
                            Text("${currentCard.phonetic} (${currentCard.concept})", fontSize = 14.sp, color = TextMuted)
                        }
                    }

                    Surface(
                        color = BackgroundLight,
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(10.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(currentCard.exampleHindi ?: "", fontSize = 13.sp)
                            Text(currentCard.exampleSantali ?: "", fontSize = 14.sp, color = AccentTeal, fontWeight = FontWeight.Bold)
                        }
                    }

                    Button(
                        onClick = {
                            Toast.makeText(context, "Playing audio for '${currentCard.santaliWord}'", Toast.LENGTH_SHORT).show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                    ) {
                        Text("🔊 Play Audio", fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Carousel Controls
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Button(
                    onClick = {
                        currentIndex = (currentIndex - 1 + cards.size) % cards.size
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryDark)
                ) {
                    Text("❮ Previous")
                }

                Text("${currentIndex + 1} of ${cards.size}", fontWeight = FontWeight.Bold)

                Button(
                    onClick = {
                        currentIndex = (currentIndex + 1) % cards.size
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryDark)
                ) {
                    Text("Next ❯")
                }
            }

            OutlinedButton(
                onClick = {
                    Toast.makeText(context, "Flashcards saved to offline storage!", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("💾 Save All Offline")
            }
        }
    }
}
