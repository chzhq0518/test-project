package com.example.agent.ui

import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Switch
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agent.R

/**
 * 设置页面 - 配置模型来源和 API 参数
 */
class SettingsActivity : AppCompatActivity() {

    private lateinit var prefs: SharedPreferences
    private lateinit var useServerSwitch: Switch
    private lateinit var baseUrlEditText: EditText
    private lateinit var openaiApiKeyEditText: EditText
    private lateinit var modelNameEditText: EditText
    private lateinit var saveButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        supportActionBar?.apply {
            setDisplayHomeAsUpEnabled(true)
            title = "设置"
        }

        prefs = getSharedPreferences("agent_settings", MODE_PRIVATE)

        setupViews()
        loadSettings()
    }

    private fun setupViews() {
        useServerSwitch = findViewById(R.id.useServerSwitch)
        baseUrlEditText = findViewById(R.id.baseUrlEditText)
        openaiApiKeyEditText = findViewById(R.id.openaiApiKeyEditText)
        modelNameEditText = findViewById(R.id.modelNameEditText)
        saveButton = findViewById(R.id.saveButton)

        useServerSwitch.setOnCheckedChangeListener { _, isChecked ->
            updateFieldsVisibility(isChecked)
        }

        saveButton.setOnClickListener {
            saveSettings()
        }
    }

    private fun loadSettings() {
        val useServer = prefs.getBoolean("use_server", true)
        val baseUrl = prefs.getString("base_url", "http://localhost:8080") ?: "http://localhost:8080"
        val apiKey = prefs.getString("openai_api_key", "") ?: ""
        val modelName = prefs.getString("model_name", "gpt-3.5-turbo") ?: "gpt-3.5-turbo"

        useServerSwitch.isChecked = useServer
        baseUrlEditText.setText(baseUrl)
        openaiApiKeyEditText.setText(apiKey)
        modelNameEditText.setText(modelName)

        updateFieldsVisibility(useServer)
    }

    private fun updateFieldsVisibility(useServer: Boolean) {
        baseUrlEditText.isEnabled = useServer
        openaiApiKeyEditText.isEnabled = !useServer
        modelNameEditText.isEnabled = !useServer
    }

    private fun saveSettings() {
        val useServer = useServerSwitch.isChecked
        val baseUrl = baseUrlEditText.text.toString().trim()
        val apiKey = openaiApiKeyEditText.text.toString().trim()
        val modelName = modelNameEditText.text.toString().trim()

        // 验证输入
        if (useServer && baseUrl.isEmpty()) {
            Toast.makeText(this, "请输入服务端 Base URL", Toast.LENGTH_SHORT).show()
            return
        }

        if (!useServer && apiKey.isEmpty()) {
            Toast.makeText(this, "请输入 OpenAI API Key", Toast.LENGTH_SHORT).show()
            return
        }

        if (!useServer && modelName.isEmpty()) {
            Toast.makeText(this, "请输入模型名称", Toast.LENGTH_SHORT).show()
            return
        }

        // 保存设置
        prefs.edit().apply {
            putBoolean("use_server", useServer)
            putString("base_url", baseUrl)
            putString("openai_api_key", apiKey)
            putString("model_name", modelName)
            apply()
        }

        Toast.makeText(this, "设置已保存，请重启应用生效", Toast.LENGTH_LONG).show()
        finish()
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
