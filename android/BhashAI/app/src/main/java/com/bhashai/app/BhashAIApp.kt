package com.bhashai.app

import android.app.Application
import android.util.Log

class BhashAIApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Log.i("BhashAI", "BhashAI Application Initialized. Target: Android 9+, Offline-Capable.")
    }
}
