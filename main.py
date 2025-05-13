from fastapi import FastAPI, HTTPException, Request, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
from typing import Optional, Dict, Any
import logging
import asyncio
from starlette.responses import StreamingResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(title="GeminiPy", description="Google Gemini API 中转服务")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API 基础 URL
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1"

# 创建 HTTP 客户端
http_client = httpx.AsyncClient(timeout=120.0)  # 设置较长的超时时间以适应长时间运行的请求

@app.get("/")
async def root():
    """服务状态检查"""
    return {"status": "running", "service": "geminipy"}

async def get_api_key(
    x_api_key: Optional[str] = Header(None),
    api_key: Optional[str] = None
):
    """从请求头或查询参数中获取 API 密钥"""
    if x_api_key:
        return x_api_key
    elif api_key:
        return api_key
    raise HTTPException(status_code=401, detail="API 密钥缺失。请在请求头 'X-API-Key' 或查询参数 'api_key' 中提供 Gemini API 密钥")

@app.post("/v1/models/{model_id}:generateContent")
async def generate_content(
    request: Request,
    model_id: str,
    api_key: str = Depends(get_api_key)
):
    """转发 generateContent 请求到 Gemini API"""
    try:
        # 获取请求体
        request_body = await request.json()
        logger.info(f"接收到 generateContent 请求: 模型={model_id}")
        
        # 构建转发 URL
        url = f"{GEMINI_BASE_URL}/models/{model_id}:generateContent?key={api_key}"
        
        # 转发请求
        response = await http_client.post(url, json=request_body)
        
        # 返回 Gemini API 的响应
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误: {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.post("/v1beta/models/{model_id}:generateContent")
async def generate_content_beta(
    request: Request,
    model_id: str,
    api_key: str = Depends(get_api_key)
):
    """转发 generateContent (beta) 请求到 Gemini API"""
    try:
        request_body = await request.json()
        logger.info(f"接收到 generateContent (beta) 请求: 模型={model_id}")
        url = f"{GEMINI_BASE_URL}/v1/models/{model_id}:generateContent?key={api_key}" # 注意：转发到 v1
        response = await http_client.post(url, json=request_body)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误 (beta): {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理 beta 请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 (beta): {str(e)}")

async def stream_generator(stream):
    """从 Gemini API 流式读取响应并转发"""
    async for chunk in stream.aiter_bytes():
        yield chunk

@app.post("/v1/models/{model_id}:streamGenerateContent")
async def stream_generate_content(
    request: Request,
    model_id: str,
    api_key: str = Depends(get_api_key)
):
    """转发 streamGenerateContent 请求到 Gemini API 并流式返回结果"""
    try:
        # 获取请求体
        request_body = await request.json()
        logger.info(f"接收到 streamGenerateContent 请求: 模型={model_id}")
        
        # 构建转发 URL
        url = f"{GEMINI_BASE_URL}/models/{model_id}:streamGenerateContent?key={api_key}"
        
        # 转发请求并获取流式响应
        response = await http_client.post(url, json=request_body, timeout=60.0)
        
        # 返回流式响应
        return StreamingResponse(
            stream_generator(response),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误: {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.post("/v1beta/models/{model_id}:streamGenerateContent")
async def stream_generate_content_beta(
    request: Request,
    model_id: str,
    api_key: str = Depends(get_api_key)
):
    """转发 streamGenerateContent (beta) 请求到 Gemini API 并流式返回结果"""
    try:
        request_body = await request.json()
        logger.info(f"接收到 streamGenerateContent (beta) 请求: 模型={model_id}")
        url = f"{GEMINI_BASE_URL}/v1/models/{model_id}:streamGenerateContent?key={api_key}" # 注意：转发到 v1
        response = await http_client.post(url, json=request_body, timeout=60.0)
        return StreamingResponse(
            stream_generator(response),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type", "application/json")
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误 (beta): {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理 beta 请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 (beta): {str(e)}")

@app.get("/v1/models")
async def list_models(
    api_key: str = Depends(get_api_key)
):
    """获取可用模型列表"""
    try:
        url = f"{GEMINI_BASE_URL}/models?key={api_key}"
        response = await http_client.get(url)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误: {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.get("/v1beta/models")
async def list_models_beta(
    api_key: str = Depends(get_api_key)
):
    """获取可用模型列表 (beta)"""
    try:
        url = f"{GEMINI_BASE_URL}/v1/models?key={api_key}" # 注意：转发到 v1
        response = await http_client.get(url)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误 (beta): {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理 beta 请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 (beta): {str(e)}")

@app.get("/v1/models/{model_id}")
async def get_model(
    model_id: str,
    api_key: str = Depends(get_api_key)
):
    """获取特定模型信息"""
    try:
        url = f"{GEMINI_BASE_URL}/models/{model_id}?key={api_key}"
        response = await http_client.get(url)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误: {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")

@app.get("/v1beta/models/{model_id}")
async def get_model_beta(
    model_id: str,
    api_key: str = Depends(get_api_key)
):
    """获取特定模型信息 (beta)"""
    try:
        url = f"{GEMINI_BASE_URL}/v1/models/{model_id}?key={api_key}" # 注意：转发到 v1
        response = await http_client.get(url)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API 错误 (beta): {str(e)}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"处理 beta 请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误 (beta): {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时关闭 HTTP 客户端"""
    await http_client.aclose()

if __name__ == "__main__":
    # 从环境变量获取端口或使用默认值
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 