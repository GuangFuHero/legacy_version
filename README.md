# API Tests

[繁體中文](README.zh-TW.md)

> ⚠️ **IMPORTANT WARNING**
>
> **🚫 DO NOT USE FOR PRODUCTION TESTING 🚫**
>
> This test suite performs CRUD operations (Create, Read, Update, Delete) that will directly modify database content.
> **Only use in Local and Development environments.**

Backend API test suite using [Hurl](https://hurl.dev).

## Project Structure

```
api-tests/
├── .env.hurl          # Environment configuration file (create your own)
├── .env.hurl.example  # Environment configuration template
├── .gitignore         # Git ignore settings
├── run_all.sh         # Run all tests
├── run_test.sh        # Run a single test
├── tests/             # Test directory
│   └── test_*.hurl    # Test files for each resource
└── README.md          # This file
```

## Prerequisites

### Install Hurl

```bash
# macOS
brew install hurl

# For other platforms: https://hurl.dev/docs/installation.html
```

## Setup

### 1. Create Environment Configuration File

Create a `.env.hurl` file in the project root directory:

```bash
# .env.hurl
base_url=http://localhost:8080
```

⚠️ **Note**: `.env.hurl` is included in `.gitignore`. Do not commit files containing actual environment information to Git.

### 2. Verify Target Environment

**Double check**: Ensure that `base_url` points to a development or testing environment. **Never point to production.**

## Running Tests

### Method 1: Using Scripts (Recommended)

```bash
# Run all tests
./run_all.sh

# Run a single test (you can omit the test_ prefix and .hurl extension)
./run_test.sh shelters
./run_test.sh health
./run_test.sh supplies
```

### Method 2: Using Hurl Directly

```bash
# Run all tests
hurl --test --variables-file .env.hurl tests/*.hurl

# Run a single test file
hurl --test --variables-file .env.hurl tests/test_health.hurl
```

## Test Files Description

| File                                | Description                                              |
| ----------------------------------- | -------------------------------------------------------- |
| `test_health.hurl`                  | Health check and system info endpoints                   |
| `test_shelters.hurl`                | Shelters CRUD                                            |
| `test_medical_stations.hurl`        | Medical stations CRUD                                    |
| `test_mental_health_resources.hurl` | Mental health resources CRUD                             |
| `test_accommodations.hurl`          | Accommodations CRUD                                      |
| `test_shower_stations.hurl`         | Shower stations CRUD                                     |
| `test_water_refill_stations.hurl`   | Water refill stations CRUD                               |
| `test_restrooms.hurl`               | Restrooms CRUD                                           |
| `test_volunteer_organizations.hurl` | Volunteer organizations CRUD                             |
| `test_human_resources.hurl`         | Human resources CRUD (includes PATCH)                    |
| `test_supplies.hurl`                | Supplies CRUD (includes supply items and batch delivery) |
| `test_reports.hurl`                 | Reports CRUD (includes PATCH)                            |
| `test_admin.hurl`                   | Admin endpoints                                          |

## Important Notes

- ✅ Each test file is independent and creates its own test data
- ✅ Some tests depend on previously created resource IDs (captured via `[Captures]`)
- ✅ Tests will create actual data in the database
- ⚠️ **Make sure to use a test environment to avoid polluting production data**
- ⚠️ **Always verify the `base_url` setting in `.env.hurl` before running tests**

## Related Resources

- [Hurl Official Documentation](https://hurl.dev/docs/manual.html)
- [Hurl Examples](https://hurl.dev/docs/samples.html)

## Security Reminder

🔒 If you need to add sensitive information (such as API keys) to `.env.hurl`:

1. Ensure `.env.hurl` is included in `.gitignore`
2. Never commit configuration files containing sensitive information to version control
3. Create `.env.hurl.example` as a template for other developers to reference
