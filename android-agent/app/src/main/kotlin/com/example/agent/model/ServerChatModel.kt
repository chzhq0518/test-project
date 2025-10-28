package com.example.agent.model

import dev.langchain4j.data.message.AiMessage
import dev.langchain4j.data.message.ChatMessage
import dev.langchain4j.model.chat.ChatLanguageModel
import dev.langchain4j.model.output.Response
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

/**
 * 服务端代理 ChatModel 实现
 * 通过 REST API 调用服务端的 /chat 接口
 */
class ServerChatModel(private val baseUrl: String) : ChatLanguageModel {

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    override fun generate(messages: MutableList<ChatMessage>): Response<AiMessage> {
        val apiMessages = messages.map { message ->
            ApiMessage(
                role = when {
                    message.type().toString() == "SYSTEM" -> "system"
                    message.type().toString() == "USER" -> "user"
                    message.type().toString() == "AI" -> "assistant"
                    else -> "user"
                },
                content = message.text()
            )
        }

        val requestBody = ChatRequest(apiMessages)
        val json = gson.toJson(requestBody)

        val request = Request.Builder()
            .url("$baseUrl/chat")
            .post(json.toRequestBody(jsonMediaType))
            .build()

        return try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    throw RuntimeException("服务端请求失败: ${response.code} ${response.message}")
                }

                val responseBody = response.body?.string()
                    ?: throw RuntimeException("响应体为空")

                val chatResponse = gson.fromJson(responseBody, ChatResponse::class.java)
                Response.from(AiMessage.from(chatResponse.content))
            }
        } catch (e: Exception) {
            throw RuntimeException("服务端调用异常: ${e.message}", e)
        }
    }

    data class ApiMessage(
        @SerializedName("role") val role: String,
        @SerializedName("content") val content: String
    )

    data class ChatRequest(
        @SerializedName("messages") val messages: List<ApiMessage>
    )

    data class ChatResponse(
        @SerializedName("content") val content: String
    )
}
