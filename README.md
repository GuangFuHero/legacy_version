# Eval by LLM - 救災平台訊息驗證系統

這是一個使用 LLM 來驗證救災平台需求通報的系統，能夠自動判斷訊息是否為有效的救災需求，並過濾惡意或混亂行為。

## 功能特色

- 🤖 使用 LLM 模型進行智慧訊息驗證
- 🔍 自動判斷訊息是否為有效救災需求
- 🛡️ 過濾惡意或刻意混亂的訊息
- 🌐 整合外部 API 進行訊息管理
- 📊 結構化的驗證結果輸出

## 系統需求

- Python 3.13+
- Ollama (本地 LLM 服務)
- 外部 API 服務 (GF_API)

## 安裝步驟

### 1. 安裝專案依賴

```bash
# 使用 curl 安裝 uv (推薦)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 驗證安裝
uv --version

# 使用 uv 安裝依賴
uv sync

# 進入虛擬環境
source .venv/bin/activate
```

### 2. 設定環境變數

創建 `.env` 檔案：

```bash
GF_API_URL=https://your-api-url.com
GF_API_KEY=your-api-key
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
```

### 3. 安裝 Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull gemma3:1b
ollama serve
```


## 使用方法

### 基本使用

### 驗證結果格式

```json
{
  "valid": "valid|warning|invalid",
  "reason": "驗證原因說明"
}
```

- `valid`: 驗證狀態
  - `valid`: 有效
  - `warning`: 需要關注
  - `invalid`: 無效或惡意訊息
- `reason`: 中文說明驗證原因

## 專案結構

```
eval-by-llm/
├── message_validator.py    # 主要驗證邏輯
├── system_prompt.txt       # LLM 系統提示詞
├── pyproject.toml         # 專案配置
├── .env                   # 環境變數 (需自行創建)
├── .gitignore            # Git 忽略檔案
└── README.md             # 專案說明
```

## 開發說明

### 系統提示詞

`system_prompt.txt` 包含了對 LLM 的指令，定義了驗證邏輯和輸出格式。你可以根據需求修改這個檔案來調整驗證行為。

### 自訂模型

可以透過修改 `.env` 中的 `OLLAMA_MODEL` 來使用不同的 LLM 模型：

## 故障排除

### Ollama 連線問題
```bash
ollama list
ollama serve
```

### API 連線問題
檢查 `.env` 檔案中的 API URL 和 Key 是否正確。

### 模型載入問題
確保指定的模型已正確下載：
```bash
ollama pull [model_name]
```