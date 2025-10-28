package com.example.agent.tools

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioManager
import android.os.Build
import android.provider.Settings
import dev.langchain4j.agent.tool.Tool

/**
 * Android 系统工具集
 * 使用 @Tool 注解定义可供 Agent 调用的方法
 */
class AndroidSystemTools(private val context: Context) {

    @Tool("获取设备信息，包括设备型号、系统版本等")
    fun getDeviceInfo(): String {
        return buildString {
            append("设备型号: ${Build.MODEL}\n")
            append("制造商: ${Build.MANUFACTURER}\n")
            append("系统版本: Android ${Build.VERSION.RELEASE}\n")
            append("SDK 版本: ${Build.VERSION.SDK_INT}\n")
            append("设备品牌: ${Build.BRAND}")
        }
    }

    @Tool("调整系统音量，参数为0-100之间的整数")
    fun adjustVolume(volumePercent: Int): String {
        return try {
            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
            val maxVolume = audioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
            val targetVolume = (maxVolume * volumePercent / 100).coerceIn(0, maxVolume)
            
            audioManager.setStreamVolume(
                AudioManager.STREAM_MUSIC,
                targetVolume,
                AudioManager.FLAG_SHOW_UI
            )
            
            "已将音量调整为 ${volumePercent}%"
        } catch (e: Exception) {
            "调整音量失败: ${e.message}"
        }
    }

    @Tool("打开指定的应用，参数为应用包名或应用名称")
    fun openApp(appName: String): String {
        return try {
            val packageManager = context.packageManager
            
            // 尝试直接使用包名
            var launchIntent = packageManager.getLaunchIntentForPackage(appName)
            
            // 如果不是包名，尝试搜索应用名称
            if (launchIntent == null) {
                val intent = Intent(Intent.ACTION_MAIN, null)
                intent.addCategory(Intent.CATEGORY_LAUNCHER)
                val apps = packageManager.queryIntentActivities(intent, 0)
                
                val targetApp = apps.find { 
                    it.loadLabel(packageManager).toString()
                        .contains(appName, ignoreCase = true) 
                }
                
                if (targetApp != null) {
                    launchIntent = Intent(Intent.ACTION_MAIN)
                    launchIntent.addCategory(Intent.CATEGORY_LAUNCHER)
                    launchIntent.setClassName(
                        targetApp.activityInfo.packageName,
                        targetApp.activityInfo.name
                    )
                    launchIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
            }
            
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(launchIntent)
                "已打开应用: $appName"
            } else {
                "未找到应用: $appName"
            }
        } catch (e: Exception) {
            "打开应用失败: ${e.message}"
        }
    }

    @Tool("获取当前电池电量信息")
    fun getBatteryLevel(): String {
        return try {
            val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as android.os.BatteryManager
            val level = batteryManager.getIntProperty(android.os.BatteryManager.BATTERY_PROPERTY_CAPACITY)
            "当前电池电量: ${level}%"
        } catch (e: Exception) {
            "获取电池信息失败: ${e.message}"
        }
    }

    @Tool("获取已安装的应用列表")
    fun getInstalledApps(): String {
        return try {
            val packageManager = context.packageManager
            val apps = packageManager.getInstalledApplications(PackageManager.GET_META_DATA)
                .filter { packageManager.getLaunchIntentForPackage(it.packageName) != null }
                .map { it.loadLabel(packageManager).toString() }
                .sorted()
                .take(20)  // 只显示前20个
            
            "已安装的应用（前20个）:\n" + apps.joinToString("\n")
        } catch (e: Exception) {
            "获取应用列表失败: ${e.message}"
        }
    }

    @Tool("打开系统设置页面")
    fun openSettings(): String {
        return try {
            val intent = Intent(Settings.ACTION_SETTINGS)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
            "已打开系统设置"
        } catch (e: Exception) {
            "打开设置失败: ${e.message}"
        }
    }
}
