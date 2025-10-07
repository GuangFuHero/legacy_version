# Human Resources API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_human_resources.hurl

# Create a human resource
POST {{base_url}}/human_resources
Content-Type: application/json
{
  "org": "Test Organization",
  "address": "花蓮縣光復鄉中正路150號",
  "phone": "03-1234574",
  "status": "active",
  "is_completed": false,
  "has_medical": false,
  "pii_date": null,
  "role_name": "清潔志工",
  "role_type": "volunteer",
  "skills": ["清掃", "整理"],
  "certifications": [],
  "experience_level": "beginner",
  "language_requirements": ["zh-TW"],
  "headcount_need": 10,
  "headcount_got": 0,
  "headcount_unit": "人",
  "role_status": "pending",
  "shift_start_ts": null,
  "shift_end_ts": null,
  "shift_notes": null,
  "assignment_timestamp": null,
  "assignment_count": null,
  "assignment_notes": null
}
HTTP 201
[Captures]
human_resource_id: jsonpath "$.id"
[Asserts]
jsonpath "$.role_name" == "清潔志工"

# List human resources
GET {{base_url}}/human_resources?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# List with filters
GET {{base_url}}/human_resources?status=active&role_status=pending&limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single human resource
GET {{base_url}}/human_resources/{{human_resource_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{human_resource_id}}"

# Patch human resource (update headcount_got)
PATCH {{base_url}}/human_resources/{{human_resource_id}}
Content-Type: application/json
{
  "headcount_got": 5
}
HTTP 200
[Asserts]
jsonpath "$.headcount_got" == 5
