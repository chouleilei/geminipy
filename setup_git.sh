#!/bin/bash

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 初始提交
git commit -m "初始提交：创建 Gemini API 中转服务"

# 添加远程仓库（需要用户提供的 GitHub 仓库 URL）
echo "请创建 GitHub 仓库，然后运行以下命令添加远程仓库并推送："
echo "git remote add origin https://github.com/yourusername/geminipy.git"
echo "git branch -M main"
echo "git push -u origin main" 