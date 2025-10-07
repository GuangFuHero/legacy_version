# Supplies API Tests
# Run with: hurl --test --variables-file .env.hurl tests/test_supplies.hurl

# Create a supply with initial item
POST {{base_url}}/supplies
Content-Type: application/json
{
  "name": "Test Supply Warehouse",
  "address": "花蓮縣光復鄉倉庫路1號",
  "phone": "03-1234575",
  "notes": "Test supply warehouse",
  "pii_date": null,
  "supplies": {
    "tag": "food",
    "name": "白米",
    "recieved_count": 10,
    "total_count": 100,
    "unit": "包"
  }
}
HTTP 201
[Captures]
supply_id: jsonpath "$.id"
[Asserts]
jsonpath "$['@type']" == "Supply"
jsonpath "$.id" exists
jsonpath "$.name" == "Test Supply Warehouse"
jsonpath "$.address" == "花蓮縣光復鄉倉庫路1號"
jsonpath "$.phone" == "03-1234575"
jsonpath "$.notes" == "Test supply warehouse"
jsonpath "$.pii_date" == null
jsonpath "$.created_at" isInteger
jsonpath "$.updated_at" isInteger
jsonpath "$.supplies" isCollection
jsonpath "$.supplies[0].id" exists
jsonpath "$.supplies[0].supply_id" == {{supply_id}}
jsonpath "$.supplies[0].name" == "白米"
jsonpath "$.supplies[0].tag" == "food"
jsonpath "$.supplies[0].recieved_count" == 10
jsonpath "$.supplies[0].total_count" == 100
jsonpath "$.supplies[0].unit" == "包"

# List supplies
GET {{base_url}}/supplies?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"
jsonpath "$.totalItems" isInteger
jsonpath "$.totalItems" >= 1
jsonpath "$.limit" == 10
jsonpath "$.offset" == 0
jsonpath "$.member" isCollection
jsonpath "$.member[0].id" exists
jsonpath "$.member[0].supplies" isCollection

# List supplies with embedded items
GET {{base_url}}/supplies?limit=10&embed=all
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"
jsonpath "$.totalItems" isInteger
jsonpath "$.member" isCollection
jsonpath "$.member[0].id" exists
jsonpath "$.member[0].name" exists
jsonpath "$.member[0].supplies" isCollection

# Get single supply
GET {{base_url}}/supplies/{{supply_id}}
HTTP 200
[Captures]
supply_item_id: jsonpath "$.supplies[0].id"
[Asserts]
jsonpath "$['@type']" == "Supply"
jsonpath "$.id" == "{{supply_id}}"
jsonpath "$.name" == "Test Supply Warehouse"
jsonpath "$.address" == "花蓮縣光復鄉倉庫路1號"
jsonpath "$.phone" == "03-1234575"
jsonpath "$.supplies" isCollection
jsonpath "$.supplies[0].id" exists
jsonpath "$.supplies[0].name" == "白米"
jsonpath "$.supplies[0].recieved_count" == 10
jsonpath "$.supplies[0].total_count" == 100

# Distribute supply items (accumulate recieved_count)
POST {{base_url}}/supplies/{{supply_id}}
Content-Type: application/json
[
  {
    "id": "{{supply_item_id}}",
    "count": 20
  }
]
HTTP 200
[Asserts]
jsonpath "$" isCollection
jsonpath "$[0].id" == "{{supply_item_id}}"
jsonpath "$[0].supply_id" == "{{supply_id}}"
jsonpath "$[0].name" == "白米"
jsonpath "$[0].recieved_count" == 30
jsonpath "$[0].total_count" == 100

# Create a standalone supply item
POST {{base_url}}/supply_items
Content-Type: application/json
{
  "supply_id": "{{supply_id}}",
  "tag": "water",
  "name": "礦泉水",
  "total_count": 500,
  "unit": "瓶"
}
HTTP 201
[Captures]
supply_item_id2: jsonpath "$.id"
[Asserts]
jsonpath "$.id" exists
jsonpath "$.id" matches "^[0-9a-f-]+$"

# List supply items
GET {{base_url}}/supply_items?limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"
jsonpath "$.totalItems" isInteger
jsonpath "$.totalItems" >= 2
jsonpath "$.limit" == 10
jsonpath "$.offset" == 0
jsonpath "$.member" isCollection
jsonpath "$.member[0].id" exists
jsonpath "$.member[0].supply_id" exists
jsonpath "$.member[0].name" exists

# List supply items for specific supply
GET {{base_url}}/supply_items?supply_id={{supply_id}}&limit=10
HTTP 200
[Asserts]
jsonpath "$['@type']" == "Collection"
jsonpath "$.totalItems" == 2
jsonpath "$.member" isCollection
jsonpath "$.member[*].supply_id" includes "{{supply_id}}"

# Get single supply item
GET {{base_url}}/supply_items/{{supply_item_id2}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{supply_item_id2}}"
jsonpath "$.supply_id" == "{{supply_id}}"
jsonpath "$.tag" == "water"
jsonpath "$.name" == "礦泉水"
jsonpath "$.recieved_count" == 0
jsonpath "$.total_count" == 500
jsonpath "$.unit" == "瓶"
