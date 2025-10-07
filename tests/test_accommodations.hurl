# Accommodations API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_accommodations.hurl

# Create an accommodation
POST {{base_url}}/accommodations
Content-Type: application/json
{
  "township": "花蓮市",
  "name": "Test Hotel",
  "has_vacancy": "yes",
  "available_period": "2025-01-01 to 2025-12-31",
  "restrictions": "無寵物",
  "contact_info": "03-1234570",
  "room_info": "雙人房5間",
  "address": "花蓮市中華路300號",
  "pricing": "免費提供給受災戶",
  "info_source": "業者主動提供",
  "notes": "Test accommodation",
  "capacity": 10,
  "status": "available",
  "registration_method": "電話預約",
  "facilities": ["wifi", "parking", "meals"],
  "distance_to_disaster_area": "5公里",
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  }
}
HTTP 201
[Captures]
accommodation_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Test Hotel"

# List accommodations
GET {{base_url}}/accommodations?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single accommodation
GET {{base_url}}/accommodations/{{accommodation_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{accommodation_id}}"
