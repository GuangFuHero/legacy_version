# Restrooms API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_restrooms.hurl

# Create a restroom
POST {{base_url}}/restrooms
Content-Type: application/json
{
  "name": "Test Restroom",
  "address": "花蓮縣光復鄉公園路10號",
  "phone": "03-1234573",
  "facility_type": "public",
  "opening_hours": "24小時開放",
  "is_free": true,
  "male_units": 3,
  "female_units": 3,
  "unisex_units": 1,
  "accessible_units": 1,
  "has_water": true,
  "has_lighting": true,
  "status": "operational",
  "cleanliness": "良好",
  "last_cleaned": null,
  "facilities": ["toilet_paper", "soap"],
  "distance_to_disaster_area": "3公里",
  "notes": "Test restroom",
  "info_source": "公所維護",
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  }
}
HTTP 201
[Captures]
restroom_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Test Restroom"

# List restrooms
GET {{base_url}}/restrooms?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single restroom
GET {{base_url}}/restrooms/{{restroom_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{restroom_id}}"
