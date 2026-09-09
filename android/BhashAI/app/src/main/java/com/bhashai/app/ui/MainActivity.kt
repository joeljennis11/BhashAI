package com.bhashai.app.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.bhashai.app.data.repository.BhashAIRepository
import com.bhashai.app.ui.navigation.BhashAINavGraph
import com.bhashai.app.ui.theme.BhashAITheme

class MainActivity : ComponentActivity() {

    private val repository = BhashAIRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BhashAITheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    val navController = rememberNavController()
                    BhashAINavGraph(
                        navController = navController,
                        repository = repository
                    )
                }
            }
        }
    }
}
