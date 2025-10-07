# Shower Stations API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_shower_stations.hurl

# Create a shower station
POST {{base_url}}/shower_stations
Content-Type: application/json
{
  "name": "Test Shower Station",
  "address": "花蓮縣光復鄉民族路50號",
  "phone": "03-1234571",
  "facility_type": "public",
  "time_slots": "08:00-20:00",
  "gender_schedule": {
    "male": ["08:00-12:00", "16:00-20:00"],
    "female": ["12:00-16:00"]
  },
  "available_period": "2025-01-01 to 2025-12-31",
  "capacity": 20,
  "is_free": true,
  "pricing": null,
  "notes": "Test shower station",
  "info_source": "公所提供",
  "status": "operational",
  "facilities": ["hot_water", "towels"],
  "distance_to_guangfu": "1公里",
  "requires_appointment": false,
  "contact_method": "電話",
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  }
}
HTTP 201
[Captures]
shower_station_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Test Shower Station"

# List shower stations
GET {{base_url}}/shower_stations?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single shower station
GET {{base_url}}/shower_stations/{{shower_station_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{shower_station_id}}"
