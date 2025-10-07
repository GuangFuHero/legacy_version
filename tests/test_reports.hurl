# Reports API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_reports.hurl
# Note: This test depends on shelter_id from test_shelters.hurl
# You can either run test_shelters.hurl first or replace {{shelter_id}} with an actual ID

# Create a test shelter first (for location_id)
POST {{base_url}}/shelters
Content-Type: application/json
{
  "name": "Test Shelter for Report",
  "location": "花蓮縣光復鄉",
  "phone": "03-9999999",
  "status": "open"
}
HTTP 201
[Captures]
shelter_id: jsonpath "$.id"

# Create a report
POST {{base_url}}/reports
Content-Type: application/json
{
  "name": "資訊錯誤回報",
  "location_type": "shelter",
  "reason": "地址錯誤",
  "notes": "實際地址與登記不符",
  "status": "pending",
  "location_id": "{{shelter_id}}"
}
HTTP 201
[Captures]
report_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "資訊錯誤回報"
jsonpath "$.status" == "pending"

# List reports
GET {{base_url}}/reports?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# List reports with status filter
GET {{base_url}}/reports?status=pending&limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single report
GET {{base_url}}/reports/{{report_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{report_id}}"

# Patch report (update status)
PATCH {{base_url}}/reports/{{report_id}}
Content-Type: application/json
{
  "status": "resolved",
  "notes": "已確認並更新資料"
}
HTTP 200
[Asserts]
jsonpath "$.status" == "resolved"
