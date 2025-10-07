# API Tests

[English](README.md)

> ⚠️ **重要警告 / IMPORTANT WARNING**
>
> **🚫 請勿用於測試生產環境 (Production) 🚫**
>
> 本測試套件會執行 CRUD 操作（新增、讀取、更新、刪除），會直接修改資料庫內容。
> **僅限用於本地環境 (Local) 和開發環境 (Development)**。
>
> **DO NOT USE FOR PRODUCTION TESTING**
>
> This test suite performs CRUD operations that will modify database content.
> **Only use in Local and Development environments.**

使用 [Hurl](https://hurl.dev) 的後端 API 測試套件。

## 專案結構

```
api-tests/
├── .env.hurl          # 環境配置檔（需自行建立）
├── .env.hurl.example  # 環境配置範本
├── .gitignore         # Git 忽略設定
├── run_all.sh         # 執行所有測試
├── run_test.sh        # 執行單一測試
├── tests/             # 測試目錄
│   └── test_*.hurl    # 各資源的測試文件
└── README.md          # 本文件
```

## 前置需求

### 安裝 Hurl

```bash
# macOS
brew install hurl

# 其他平台請參考: https://hurl.dev/docs/installation.html
```

## 設定

### 1. 建立環境配置檔

在專案根目錄建立 `.env.hurl` 檔案：

```bash
# .env.hurl
base_url=http://localhost:8080
```

⚠️ **注意**: `.env.hurl` 已加入 `.gitignore`，請勿將包含實際環境資訊的檔案提交到 Git。

### 2. 確認目標環境

**再次確認**: 請確保 `base_url` 指向本地或開發環境，**絕不要指向生產環境**。

## 執行測試

### 方法一：使用腳本（推薦）

```bash
# 執行所有測試
./run_all.sh

# 執行單一測試（可省略 test_ 前綴和 .hurl 副檔名）
./run_test.sh shelters
./run_test.sh health
./run_test.sh supplies
```

### 方法二：直接使用 Hurl

```bash
# 執行所有測試
hurl --test --variables-file .env.hurl tests/*.hurl

# 執行單一測試文件
hurl --test --variables-file .env.hurl tests/test_health.hurl
```

## 測試文件說明

| 檔案                                | 說明                                  |
| ----------------------------------- | ------------------------------------- |
| `test_health.hurl`                  | 健康檢查與系統資訊端點                |
| `test_shelters.hurl`                | 避難所 CRUD                           |
| `test_medical_stations.hurl`        | 醫療站 CRUD                           |
| `test_mental_health_resources.hurl` | 心理健康資源 CRUD                     |
| `test_accommodations.hurl`          | 住宿 CRUD                             |
| `test_shower_stations.hurl`         | 淋浴站 CRUD                           |
| `test_water_refill_stations.hurl`   | 飲水站 CRUD                           |
| `test_restrooms.hurl`               | 廁所 CRUD                             |
| `test_volunteer_organizations.hurl` | 志工組織 CRUD                         |
| `test_human_resources.hurl`         | 人力資源 CRUD（含 PATCH）             |
| `test_supplies.hurl`                | 物資供應 CRUD（含物資項目與批次配送） |
| `test_reports.hurl`                 | 回報 CRUD（含 PATCH）                 |
| `test_admin.hurl`                   | 管理端點                              |

## 注意事項

- ✅ 每個測試文件都是獨立的，會建立自己的測試資料
- ✅ 某些測試會依賴先前建立的資源 ID（透過 `[Captures]` 擷取）
- ✅ 測試會在資料庫中建立實際資料
- ⚠️ **請確保使用測試環境，避免污染生產資料**
- ⚠️ **執行測試前務必確認 `.env.hurl` 中的 `base_url` 設定**

## 相關資源

- [Hurl 官方文件](https://hurl.dev/docs/manual.html)
- [Hurl 範例](https://hurl.dev/docs/samples.html)

## 安全提醒

🔒 如果你需要在 `.env.hurl` 中加入敏感資訊（如 API 金鑰），請：

1. 確認 `.env.hurl` 已在 `.gitignore` 中
2. 絕不要將包含敏感資訊的設定檔提交到版本控制系統
3. 可建立 `.env.hurl.example` 作為範本供其他開發者參考
