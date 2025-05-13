# GeminiPy

GeminiPy 是一个用于 Google Gemini API 的中转服务，可部署在 Google Cloud Run 上。用户可以通过提供自己的 API 密钥来使用该服务，无需额外配置。

## 特性

- 支持 Gemini API 的主要功能（生成内容、流式生成、模型列表）
- 用户提供自己的 API 密钥
- 简单的身份验证系统
- 支持 CORS
- 适合部署在 Google Cloud Run 上

## 部署说明

### 本地开发

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/geminipy.git
   cd geminipy
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行服务：
   ```bash
   python main.py
   ```

服务将在 http://localhost:8080 启动。

### 部署到 Google Cloud Run

1. 确保您已经设置了 Google Cloud 账户，并安装了 [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)。

2. 通过 GitHub 连接部署：

   a. 在 Google Cloud 控制台中，转到 Cloud Run。
   
   b. 点击"创建服务"。
   
   c. 选择"持续部署从源代码库"。
   
   d. 连接到您的 GitHub 仓库，选择 `geminipy` 仓库。
   
   e. 配置构建：选择 Dockerfile 作为构建方法。
   
   f. 配置服务：选择区域、内存、CPU 等资源设置。
   
   g. 点击"创建"完成部署。

## 使用说明

### API 端点

- `GET /` - 服务状态检查
- `GET /v1/models` - 获取可用模型列表
- `GET /v1/models/{model_id}` - 获取特定模型信息
- `POST /v1/models/{model_id}:generateContent` - 生成内容
- `POST /v1/models/{model_id}:streamGenerateContent` - 流式生成内容

### 身份验证

向所有请求提供您的 Gemini API 密钥，可以通过以下两种方式：

1. 请求头：`X-API-Key: your_api_key`
2. 查询参数：`?api_key=your_api_key`

### 示例请求

```bash
# 获取模型列表
curl -X GET "https://your-cloud-run-url.run.app/v1/models" \
  -H "X-API-Key: YOUR_GEMINI_API_KEY"

# 生成内容
curl -X POST "https://your-cloud-run-url.run.app/v1/models/gemini-pro:generateContent" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_GEMINI_API_KEY" \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "写一首关于人工智能的诗"
          }
        ]
      }
    ]
  }'
```

## 注意事项

- 本服务仅作为中转代理，不会存储您的 API 密钥或请求数据
- 您需要遵守 Google Gemini API 的使用条款
- 在生产环境中，建议限制 CORS 来源和添加更多的安全措施

## 许可

MIT 