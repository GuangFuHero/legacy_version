# Water Refill Stations API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_water_refill_stations.hurl

# Create a water refill station
POST {{base_url}}/water_refill_stations
Content-Type: application/json
{
  "name": "Test Water Station",
  "address": "花蓮縣光復鄉中山路80號",
  "phone": "03-1234572",
  "water_type": "filtered",
  "opening_hours": "24小時開放",
  "is_free": true,
  "container_required": "請自備容器",
  "daily_capacity": 5000,
  "status": "operational",
  "water_quality": "已檢驗合格",
  "facilities": ["parking"],
  "accessibility": true,
  "distance_to_disaster_area": "2公里",
  "notes": "Test water station",
  "info_source": "公所設置",
  "coordinates": {
    "lat": 23.8,
    "lng": 121.4
  }
}
HTTP 201
[Captures]
water_station_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" == "Test Water Station"

# List water refill stations
GET {{base_url}}/water_refill_stations?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"

# Get single water refill station
GET {{base_url}}/water_refill_stations/{{water_station_id}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{water_station_id}}"
