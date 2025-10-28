# LangChain4j Android Agent

基于 LangChain4j 的 Android 智能代理骨架项目，支持工具调用、对话记忆和可切换的模型来源。

## 功能特性

### ✅ 已实现功能

- **Agent 核心**
  - 基于 LangChain4j 框架
  - 内置 `MessageWindowChatMemory`，保留最近10条对话历史
  - 自动工具调用能力

- **双模型支持**
  - 🔹 **服务端代理模式**：通过 REST API 调用自定义服务端
  - 🔹 **OpenAI 直连模式**：直接连接 OpenAI API
  - 设置页可动态切换

- **Android 系统工具集**
  - 📱 获取设备信息（型号、制造商、系统版本）
  - 🔊 调整系统音量
  - 🔋 获取电池电量
  - 📦 获取已安装应用列表
  - 🚀 打开指定应用
  - ⚙️ 打开系统设置

- **用户界面**
  - 💬 聊天对话界面
  - ⚡ 快捷命令按钮
  - ⚙️ 设置页面
  - 🧹 清空对话功能

## 技术栈

- **语言**：Kotlin
- **UI 框架**：AndroidX + Material Design 3
- **AI 框架**：LangChain4j 0.35.0
- **网络**：OkHttp 4.12.0
- **序列化**：Gson 2.10.1
- **异步**：Kotlin Coroutines
- **最低 SDK**：Android 8.0 (API 26)
- **目标 SDK**：Android 14 (API 34)

## 快速开始

### 1. 克隆项目

```bash
cd android-agent
```

### 2. 编译项目

```bash
./gradlew build
```

### 3. 安装到设备

```bash
./gradlew installDebug
```

或者在 Android Studio 中打开项目，直接运行。

## 配置说明

### 服务端代理模式

1. 在设置页开启“使用服务端代理”
2. 输入服务端 Base URL（例：`http://your-server.com:8080`）
3. 保存设置并重启应用

#### 服务端接口约定

**请求**：`POST {baseUrl}/chat`

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**响应**：

```json
{
  "content": "最终回复文本"
}
```

### OpenAI 直连模式

1. 在设置页关闭“使用服务端代理”
2. 输入 OpenAI API Key
3. 输入模型名称（例：`gpt-3.5-turbo`、`gpt-4`）
4. 保存设置并重启应用

## 示例命令

在聊天界面可以尝试以下命令：

```
获取设备信息
调整音量到50%
获取电池电量
获取已安装应用
打开设置
打开微信
```

## 项目结构

```
android-agent/
├── app/
│   ├── src/main/
│   │   ├── kotlin/com/example/agent/
│   │   │   ├── core/
│   │   │   │   └── AndroidAgent.kt         # Agent 核心类
│   │   │   ├── model/
│   │   │   │   └── ServerChatModel.kt      # 服务端模型实现
│   │   │   ├── tools/
│   │   │   │   └── AndroidSystemTools.kt   # 系统工具集
│   │   │   ├── ui/
│   │   │   │   ├── MainActivity.kt        # 主界面
│   │   │   │   ├── SettingsActivity.kt    # 设置页面
│   │   │   │   └── ChatAdapter.kt         # 聊天适配器
│   │   │   └── data/
│   │   │       └── ChatMessage.kt         # 消息数据类
│   │   ├── res/                          # 资源文件
│   │   └── AndroidManifest.xml           # 清单文件
│   └── build.gradle                    # App 模块配置
├── build.gradle                        # 项目配置
├── settings.gradle                     # 项目设置
└── README.md                           # 项目说明
```

## 扩展工具

在 `AndroidSystemTools.kt` 中添加新的 `@Tool` 方法：

```kotlin
@Tool("工具描述")
fun yourToolMethod(param: String): String {
    // 实现逻辑
    return "返回结果"
}
```

Agent 会自动识别并调用该工具。

## 注意事项

1. **安全性**：
   - 不要在客户端固化 API Key
   - 推荐使用服务端代理模式
   - 服务端应实现限流和鉴权

2. **权限**：
   - 应用需要网络权限
   - 音量控制需要 `MODIFY_AUDIO_SETTINGS` 权限
   - 查询应用列表需要 `QUERY_ALL_PACKAGES` 权限

3. **性能**：
   - AI 调用是异步执行，不会阻塞 UI
   - 记忆窗口限制为10条消息，可调整

4. **网络**：
   - 默认允许明文 HTTP 连接（`usesCleartextTraffic="true"`）
   - 生产环境建议使用 HTTPS

## 后续扩展计划

- [ ] RAG （检索增强生成）支持
- [ ] 更多 Android 系统工具
- [ ] 无障碍服务集成
- [ ] 语音输入/输出支持
- [ ] 本地小模型支持
- [ ] 更丰富的对话管理

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue 或联系项目维护者。
