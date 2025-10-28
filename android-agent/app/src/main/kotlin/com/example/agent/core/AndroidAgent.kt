package com.example.agent.core

import android.content.Context
import android.content.SharedPreferences
import dev.langchain4j.agent.tool.ToolSpecification
import dev.langchain4j.memory.ChatMemory
import dev.langchain4j.memory.chat.MessageWindowChatMemory
import dev.langchain4j.model.chat.ChatLanguageModel
import dev.langchain4j.model.openai.OpenAiChatModel
import dev.langchain4j.service.AiServices
import com.example.agent.model.ServerChatModel
import com.example.agent.tools.AndroidSystemTools

/**
 * Android Agent 核心类
 * 集成 LangChain4j，支持工具调用、对话记忆和模型切换
 */
class AndroidAgent(private val context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("agent_settings", Context.MODE_PRIVATE)
    private val chatMemory: ChatMemory = MessageWindowChatMemory.withMaxMessages(10)
    private val systemTools = AndroidSystemTools(context)

    private var assistant: AgentAssistant? = null

    /**
     * 初始化 Agent，根据设置选择模型来源
     */
    fun initialize() {
        val chatModel = createChatModel()
        
        assistant = AiServices.builder(AgentAssistant::class.java)
            .chatLanguageModel(chatModel)
            .chatMemory(chatMemory)
            .tools(systemTools)
            .build()
    }

    /**
     * 创建聊天模型（服务端优先）
     */
    private fun createChatModel(): ChatLanguageModel {
        val useServer = prefs.getBoolean("use_server", true)
        
        return if (useServer) {
            // 使用服务端代理
            val baseUrl = prefs.getString("base_url", "http://localhost:8080") ?: "http://localhost:8080"
            ServerChatModel(baseUrl)
        } else {
            // 使用 OpenAI 直连
            val apiKey = prefs.getString("openai_api_key", "") ?: ""
            val modelName = prefs.getString("model_name", "gpt-3.5-turbo") ?: "gpt-3.5-turbo"
            
            if (apiKey.isEmpty()) {
                throw IllegalStateException("OpenAI API Key 未配置")
            }
            
            OpenAiChatModel.builder()
                .apiKey(apiKey)
                .modelName(modelName)
                .temperature(0.7)
                .build()
        }
    }

    /**
     * 发送消息给 Agent
     */
    fun chat(message: String): String {
        if (assistant == null) {
            initialize()
        }
        
        return try {
            assistant?.chat(message) ?: "Agent 未初始化"
        } catch (e: Exception) {
            "错误: ${e.message}"
        }
    }

    /**
     * 重置对话记忆
     */
    fun clearMemory() {
        chatMemory.clear()
    }

    /**
     * 重新加载配置
     */
    fun reload() {
        assistant = null
        initialize()
    }

    /**
     * Agent 助手接口
     */
    interface AgentAssistant {
        fun chat(message: String): String
    }
}
