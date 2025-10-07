# Shelters API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_shelters.hurl

# Create a shelter
POST {{base_url}}/shelters
Content-Type: application/json
{
  "name": "Test Shelter",
  "location": "花蓮縣光復鄉",
  "phone": "03-1234567",
  "status": "open",
  "capacity": 100,
  "current_occupancy": 50,
  "available_spaces": 50,
  "facilities": ["wifi", "meals", "medical"],
  "contact_person": "張三",
  "notes": "Test shelter note",
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  },
  "opening_hours": "24小時開放"
}
HTTP 201
[Captures]
shelter_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Test Shelter"
jsonpath "$.status" == "open"

# List shelters
GET {{base_url}}/shelters?limit=10&offset=0
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"
jsonpath "$.totalItems" > 0

# List shelters with status filter
GET {{base_url}}/shelters?status=open&limit=5
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single shelter
GET {{base_url}}/shelters/{{shelter_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{shelter_id}}"
jsonpath "$.name" == "Test Shelter"
