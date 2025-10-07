# Health Check & Info Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_health.hurl

GET {{base_url}}/healthz
HTTP 200
[Asserts]
jsonpath "$.status" == "ok"

GET {{base_url}}/openapi.yaml
HTTP 200

GET {{base_url}}/sheet/snapshot
HTTP 200
