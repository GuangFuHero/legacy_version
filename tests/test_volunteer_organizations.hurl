# Volunteer Organizations API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_volunteer_organizations.hurl

# Create a volunteer organization
POST {{base_url}}/volunteer_organizations
Content-Type: application/json
{
  "registration_status": "registered",
  "organization_nature": "NGO",
  "organization_name": "Test Volunteer Org",
  "coordinator": "王小明",
  "contact_info": "0912-345678",
  "registration_method": "線上報名",
  "service_content": "清掃、物資搬運",
  "meeting_info": "每週六上午9點集合",
  "notes": "Test volunteer org",
  "image_url": "https://example.com/image.jpg"
}
HTTP 201
[Captures]
volunteer_org_id: jsonpath "$.id"
[Asserts]
jsonpath "$.organization_name" == "Test Volunteer Org"

# List volunteer organizations
GET {{base_url}}/volunteer_organizations?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single volunteer organization
GET {{base_url}}/volunteer_organizations/{{volunteer_org_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{volunteer_org_id}}"
