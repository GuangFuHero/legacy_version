# Admin Endpoints Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_admin.hurl

# List request logs
GET {{base_url}}/_admin/request_logs?limit=20
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"
