# Spam Blocker - 救災平台訊息驗證系統

這是一個使用 LLM 來驗證救災平台需求通報的系統，能夠自動判斷訊息是否為有效的救災需求，並過濾惡意或混亂行為。

## 功能特色

- 🤖 使用 LLM 模型進行智慧訊息驗證
- 🔍 自動判斷訊息是否為有效救災需求
- 🛡️ 過濾惡意或刻意混亂的訊息
- 🌐 整合外部 API 進行訊息管理
- 📊 結構化的驗證結果輸出
- 🚀 使用 Redis Message Queue 進行非同步處理
- 📝 驗證結果分別傳送到 google sheet、guanfu go be 以及私人 discord server
- 🔄 定時排程抓取和處理新資料

## 系統架構

系統採用模組化設計，分為以下組件：

### `wokers/` - Worker 模組
- **RecordFetcher**: 從 API 抓取資料並過濾重複記錄
- **RecordProcessor**: 驗證記錄並上傳結果

### `message_queue/` - Message Queue 模組  
- **MessageQueueProcessor**: Redis Queue 管理
- **Scheduler**: 定時任務排程
- **ProcessedRecordTracker**: 已處理記錄追蹤

### `lib/` - 核心函式庫
- **GfApiClient**: 光復救災平台 API 客戶端
- **OllamaClient**: Ollama LLM 驗證客戶端
- **GoogleSheetHandler**: Google Sheets 整合
```

## 系統需求

- Docker 和 Docker Compose
- Ollama (在 host 機器上運行)
- Google Cloud 服務帳戶憑證

## 安裝步驟

### 1. 安裝必要軟體

#### 安裝 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose -y

# 將當前使用者加入 docker 群組
sudo usermod -aG docker $USER
```

#### 安裝並啟動 Ollama

```bash
# 安裝 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下載模型
ollama pull gemma3:1b

# 啟動 Ollama 服務（背景執行）
ollama serve &
```

### 2. 設定環境變數

創建 `.env` 檔案：

```bash
# GF API 設定
GF_API_URL=https://your-api-url.com
GF_API_KEY=your-api-key

# Ollama 設定（Docker 內部存取 host）
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=gemma3:1b

# Google Sheets 設定
GOOGLE_SHEET_ID=your-google-sheet-id

# 抓取設定
FETCH_LIMIT=50
OFFSET=0
```

### 3. 準備 Google Credentials

系統需要 Google Cloud 服務帳戶憑證來存取 Google Sheets。在建構 Docker 映像前，需先準備憑證檔案。

```bash
# 1. 創建 secret 目錄
mkdir -p secret

# 2. 將 Google Cloud 服務帳戶憑證轉換為 base64 並儲存
base64 -w 0 path/to/your/credentials.json > secret/cred.txt
```

**Docker 建構過程說明：**
- Dockerfile 會在建構時自動執行以下步驟：
  1. 複製 `secret/cred.txt` 到容器中
  2. 解碼 base64 內容並轉換為 `secret/cred.json`
  3. 刪除臨時的 `cred.txt` 檔案（保護憑證安全）

### 啟動服務

```bash
# 啟動所有服務（Redis + App）
docker compose up -d

# 查看日誌
docker compose logs -f

# 只查看 app 日誌
docker compose logs -f app

# 停止服務
docker compose down

# 停止服務並刪除 volume（清除 Redis 資料）
docker compose down -v
```

### 開發模式

```bash
# 重新建構映像
docker compose build

# 重新啟動服務
docker compose restart app

# 進入容器
docker compose exec app /bin/bash
```

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
spam-blocker/
├── src/
│   ├── wokers/                    # Worker 模組
│   │   ├── RecordFetcher.py      # 資料抓取器
│   │   └── RecordProcessor.py    # 記錄處理器
│   ├── message_queue/            # Message Queue 模組
│   │   ├── MessageQueueProcessor.py  # Queue 管理
│   │   ├── Scheduler.py          # 排程器
│   │   └── ProcessedRecordTracker.py # 記錄追蹤
│   ├── lib/                      # 核心函式庫
│   │   ├── GfApiClient.py       # API 客戶端
│   │   ├── OllamaClient.py      # LLM 客戶端
│   │   └── GoogleSheetHandler.py # Google Sheets 整合
│   ├── prompt/                   # LLM 提示詞
│   │   └── system_prompts.py    # 系統提示詞定義
│   └── main.py                   # 主程式進入點
├── docker-compose.yml            # Docker Compose 設定
├── Dockerfile                    # Docker 映像設定
├── pyproject.toml               # Python 專案配置
├── .env                         # 環境變數 (需自行創建)
└── README.md                    # 專案說明
```

## 開發說明

### 本地開發（不使用 Docker）

```bash
# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安裝依賴
uv sync

# 啟動 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 執行程式
uv run python src/main.py
```

### 系統提示詞

`src/prompt/system_prompts.py` 包含了對 LLM 的指令，定義了驗證邏輯和輸出格式。你可以根據需求修改這個檔案來調整驗證行為。

### 自訂模型

可以透過修改 `.env` 中的 `OLLAMA_MODEL` 來使用不同的 LLM 模型：

# 在 .env 中設定
OLLAMA_MODEL=gemma3:12b
```

### 查看 Redis 資料

```bash
# 連接到 Redis
docker compose exec redis redis-cli

# 查看所有 key
KEYS *

# 查看 queue 大小
LLEN human_resource_validation_queue
LLEN supplies_validation_queue

# 查看已處理記錄數
SCARD processed_records
```

## 故障排除

### Docker 容器無法啟動

```bash
# 檢查容器狀態
docker compose ps

# 查看完整日誌
docker compose logs

# 重新建構並啟動
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Ollama 連線問題

```bash
# 確認 Ollama 正在運行
ollama list
ps aux | grep ollama

# 重新啟動 Ollama
pkill ollama
ollama serve &

# 測試連線
curl http://localhost:11434/api/tags
```

### Redis 連線問題

```bash
# 檢查 Redis 健康狀態
docker compose exec redis redis-cli ping

# 重新啟動 Redis
docker compose restart redis
```

### API 連線問題

檢查 `.env` 檔案中的 API URL 和 Key 是否正確：

```bash
# 測試 API 連線
curl -H "Authorization: Bearer $GF_API_KEY" $GF_API_URL
```

### Google Sheets 認證問題

```bash
# 確認 credentials 檔案存在
ls -la secret/

# 重新生成 base64
base64 -w 0 path/to/credentials.json > secret/cred.txt

# 重新建構容器
docker compose build app
docker compose up -d app
```

### 清除所有資料並重新開始

```bash
# 停止並刪除所有容器和 volume
docker compose down -v

# 刪除映像
docker rmi spam-blocker-app

# 重新啟動
docker compose up -d
```

## 監控和維護

### 查看系統狀態

```bash
# 查看處理統計
docker compose logs app | grep "統計"

# 查看 Queue 大小
docker compose logs app | grep "Queue 大小"

# 即時監控
watch -n 5 'docker compose logs --tail=20 app'
```

### 日誌管理

日誌檔案儲存在 `./logs/main.log`，使用 RotatingFileHandler 自動管理：
- 最大檔案大小：5MB
- 保留最近 5 個檔案

```bash
# 查看日誌
tail -f logs/main.log
