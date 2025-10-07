# Mental Health Resources API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_mental_health_resources.hurl

# Create a mental health resource
POST {{base_url}}/mental_health_resources
Content-Type: application/json
{
  "duration_type": "long_term",
  "name": "心理諮商中心",
  "service_format": "in_person",
  "service_hours": "週一至週五 09:00-17:00",
  "contact_info": "03-1234569",
  "website_url": "https://example.com",
  "target_audience": ["adults", "children"],
  "specialties": ["trauma", "grief"],
  "languages": ["zh-TW", "en"],
  "is_free": true,
  "location": "花蓮市中山路200號",
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  },
  "status": "available",
  "capacity": 20,
  "waiting_time": "1週內",
  "notes": "Test mental health resource",
  "emergency_support": true
}
HTTP 201
[Captures]
mental_health_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "心理諮商中心"

# List mental health resources
GET {{base_url}}/mental_health_resources?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single mental health resource
GET {{base_url}}/mental_health_resources/{{mental_health_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{mental_health_id}}"
