# Medical Stations API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_medical_stations.hurl

# Create a medical station
POST {{base_url}}/medical_stations
Content-Type: application/json
{
  "station_type": "clinic",
  "name": "Test Medical Station",
  "location": "花蓮縣光復鄉中正路100號",
  "detailed_address": "一樓診間",
  "phone": "03-1234568",
  "contact_person": "李醫師",
  "status": "operational",
  "services": ["general", "emergency"],
  "operating_hours": "08:00-17:00",
  "equipment": ["ECG", "X-ray"],
  "medical_staff": 5,
  "daily_capacity": 50,
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  },
  "affiliated_organization": "花蓮醫院",
  "notes": "Test medical station"
}
HTTP 201
[Captures]
medical_station_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Test Medical Station"

# List medical stations
GET {{base_url}}/medical_stations?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single medical station
GET {{base_url}}/medical_stations/{{medical_station_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{medical_station_id}}"
