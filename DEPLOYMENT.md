# Gemini API 中转服务部署指南

本文档提供了将 GeminiPy 服务部署到 Google Cloud Run 的详细步骤。

## 前提条件

1. 一个有效的 Google Cloud 账户
2. 安装了 [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. 安装了 [Git](https://git-scm.com/downloads)
4. 一个 GitHub 账户

## 部署步骤

### 1. 准备 GitHub 仓库

1. 在 GitHub 上创建一个名为 `geminipy` 的新仓库
2. 将本地代码推送到 GitHub 仓库：

```bash
# 如果尚未初始化 Git 仓库，请运行 setup_git.sh 脚本
chmod +x setup_git.sh
./setup_git.sh

# 添加远程仓库并推送
git remote add origin https://github.com/yourusername/geminipy.git
git branch -M main
git push -u origin main
```

### 2. 设置 Google Cloud 项目

1. 登录 Google Cloud 控制台：https://console.cloud.google.com/
2. 创建一个新项目或选择现有项目
3. 启用必要的 API：
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Secret Manager API（如果需要存储敏感数据）

### 3. 通过 GitHub 连接部署到 Cloud Run

1. 在 Google Cloud 控制台中，导航到 Cloud Run
2. 点击"创建服务"
3. 选择"持续部署从源代码库"
4. 点击"设置连接到 GitHub"
5. 授权 Google Cloud 访问您的 GitHub 账户
6. 选择 `geminipy` 仓库
7. 选择分支（通常是 `main`）
8. 构建配置：
   - 选择 "Dockerfile" 作为构建类型
   - 构建目录保留为根目录 "/"
9. 服务设置：
   - 服务名称：`geminipy`
   - 区域：选择最接近您用户的区域
   - 身份验证：如果您希望服务公开可用，选择"允许未经验证的调用"
   - 入口点：保留默认值
10. 高级设置（可选）：
    - 内存：建议至少 256MB
    - CPU：可以开始使用 1 CPU
    - 自动扩缩：根据预期负载配置最小和最大实例数
11. 点击"创建"开始部署过程

### 4. 验证部署

1. 部署完成后，Cloud Run 将提供一个服务 URL
2. 使用以下命令测试服务是否正常运行：

```bash
curl -X GET "https://your-service-url.run.app/"
```

3. 如果返回 `{"status":"running","service":"geminipy"}`，则表示服务已成功部署

### 5. 使用服务

按照 README.md 中的说明使用服务。记住，您需要提供自己的 Gemini API 密钥才能使用此中转服务。

### 6. 持续部署

现在，每当您向 GitHub 仓库的 main 分支推送更改时，Cloud Run 将自动构建并部署新版本的服务。

## 故障排除

- 如果构建失败，请检查 Cloud Build 历史记录以查看错误日志
- 如果服务部署成功但无法访问，请检查 Cloud Run 日志
- 确保已为项目启用了所有必要的 API
- 检查服务配置中的入站流量设置是否允许公共访问（如果需要）

## 安全建议

- 在生产环境中，建议限制 CORS 来源
- 考虑添加额外的身份验证层，例如 API 密钥或 OAuth
- 使用 Google Cloud 的 Secret Manager 来存储敏感配置
- 定期更新依赖项以修复安全漏洞 