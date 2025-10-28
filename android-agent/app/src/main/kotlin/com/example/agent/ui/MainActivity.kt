package com.example.agent.ui

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.agent.R
import com.example.agent.core.AndroidAgent
import com.example.agent.data.ChatMessage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 主界面 - 聊天交互界面
 */
class MainActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var inputEditText: EditText
    private lateinit var sendButton: Button
    private lateinit var chatAdapter: ChatAdapter
    private lateinit var agent: AndroidAgent

    private val messages = mutableListOf<ChatMessage>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupViews()
        setupAgent()
        setupQuickCommands()
        
        // 添加欢迎消息
        addMessage(ChatMessage(
            content = "欢迎使用 LangChain4j Android Agent！\n\n您可以尝试以下命令：\n- 获取设备信息\n- 调整音量到50%\n- 获取电池电量\n- 获取已安装应用",
            isUser = false
        ))
    }

    private fun setupViews() {
        recyclerView = findViewById(R.id.recyclerView)
        inputEditText = findViewById(R.id.inputEditText)
        sendButton = findViewById(R.id.sendButton)

        chatAdapter = ChatAdapter(messages)
        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = chatAdapter
        }

        sendButton.setOnClickListener {
            sendMessage()
        }
    }

    private fun setupAgent() {
        agent = AndroidAgent(applicationContext)
        
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                agent.initialize()
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(
                        this@MainActivity,
                        "Agent 初始化失败: ${e.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }

    private fun setupQuickCommands() {
        findViewById<Button>(R.id.btnDeviceInfo).setOnClickListener {
            inputEditText.setText("获取设备信息")
            sendMessage()
        }

        findViewById<Button>(R.id.btnVolume).setOnClickListener {
            inputEditText.setText("调整音量到50%")
            sendMessage()
        }

        findViewById<Button>(R.id.btnBattery).setOnClickListener {
            inputEditText.setText("获取电池电量")
            sendMessage()
        }
    }

    private fun sendMessage() {
        val userMessage = inputEditText.text.toString().trim()
        if (userMessage.isEmpty()) {
            return
        }

        // 添加用户消息
        addMessage(ChatMessage(content = userMessage, isUser = true))
        inputEditText.text.clear()

        // 显示加载中
        sendButton.isEnabled = false

        // 异步调用 Agent
        lifecycleScope.launch(Dispatchers.IO) {
            val response = try {
                agent.chat(userMessage)
            } catch (e: Exception) {
                "错误: ${e.message}"
            }

            withContext(Dispatchers.Main) {
                addMessage(ChatMessage(content = response, isUser = false))
                sendButton.isEnabled = true
            }
        }
    }

    private fun addMessage(message: ChatMessage) {
        messages.add(message)
        chatAdapter.notifyItemInserted(messages.size - 1)
        recyclerView.scrollToPosition(messages.size - 1)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_settings -> {
                startActivity(Intent(this, SettingsActivity::class.java))
                true
            }
            R.id.action_clear -> {
                messages.clear()
                chatAdapter.notifyDataSetChanged()
                agent.clearMemory()
                Toast.makeText(this, "已清空聊天记录", Toast.LENGTH_SHORT).show()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}
