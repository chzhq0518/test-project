# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# Keep LangChain4j classes
-keep class dev.langchain4j.** { *; }
-keepclassmembers class dev.langchain4j.** { *; }

# Keep Tool annotations
-keepattributes *Annotation*
-keep @dev.langchain4j.agent.tool.Tool class * { *; }

# OkHttp
-dontwarn okhttp3.**
-keep class okhttp3.** { *; }

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.google.gson.** { *; }
