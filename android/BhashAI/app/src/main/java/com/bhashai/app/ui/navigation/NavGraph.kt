package com.bhashai.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.bhashai.app.data.repository.BhashAIRepository
import com.bhashai.app.ui.screens.*

@Composable
fun BhashAINavGraph(
    navController: NavHostController,
    repository: BhashAIRepository
) {
    NavHost(
        navController = navController,
        startDestination = "splash"
    ) {
        composable("splash") {
            SplashScreen(onNavigateToHome = {
                navController.navigate("home") {
                    popUpTo("splash") { inclusive = true }
                }
            })
        }
        composable("home") {
            HomeScreen(
                isOffline = false,
                onNavigate = { route -> navController.navigate(route) }
            )
        }
        composable("voice") {
            VoiceTranslatorScreen(
                repository = repository,
                onBack = { navController.popBackStack() }
            )
        }
        composable("text") {
            TextTranslatorScreen(
                repository = repository,
                onBack = { navController.popBackStack() }
            )
        }
        composable("lessons") {
            LessonMaterialsScreen(
                repository = repository,
                onBack = { navController.popBackStack() },
                onOpenWorksheet = { navController.navigate("worksheets") }
            )
        }
        composable("worksheets") {
            WorksheetGeneratorScreen(
                repository = repository,
                onBack = { navController.popBackStack() }
            )
        }
        composable("flashcards") {
            FlashcardsScreen(
                repository = repository,
                onBack = { navController.popBackStack() }
            )
        }
        composable("offline") {
            OfflineModelsScreen(
                repository = repository,
                onBack = { navController.popBackStack() }
            )
        }
        composable("settings") {
            SettingsScreen(
                repository = repository,
                onBack = { navController.popBackStack() }
            )
        }
        composable("about") {
            AboutScreen(onBack = { navController.popBackStack() })
        }
    }
}
