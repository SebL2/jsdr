# Progress and Goals

## Implementation Status

### Core Services & Data

#### Endpoints and CRUD
- **Objective**: Create an API server for a geographic database; Implement CRUD operations.
- **State**: Complete
- **Code Reference**: `server/endpoints.py` registers CRUD routes for cities.

#### MongoDB (Local and Cloud)
- **Objective**: Use MongoDB locally; Connect to MongoDB in the cloud.
- **State**: Complete
- **Code Reference**: `data/db_connect.py` connects locally by default and supports Atlas via `CLOUD_MONGO` env var; supports `certifi` for PythonAnywhere environment.

#### Caching in RAM
- **Objective**: Data cached in RAM.
- **State**: Complete
- **Code Reference**: `data/db_connect.py` implements `_cache` and `cached_read` function.

#### Python Decorators
- **Objective**: Use Python decorators.
- **State**: Complete
- **Code Reference**: `data/db_connect.needs_db` decorator enforces Mongo connectivity.

### Quality & Automation

#### Testing Coverage
- **Objective**: Each endpoint and other functions have unit tests.
- **State**: Complete
- **Code Reference**: API tests in `server/tests/` and unit tests in `cities/tests` and `states/tests`.

#### CI/CD
- **Objective**: GitHub Actions; Deployable to the cloud using CI/CD.
- **State**: Complete
- **Code Reference**: `.github/workflows/main.yml` runs tests and deploys to PythonAnywhere on push/PR to master.

### Deployment & Documentation

#### Swagger/OpenAPI
- **Objective**: Each endpoint documented for Swagger.
- **State**: Complete
- **Code Reference**: Flask-RESTX `Api` in `server/endpoints.py` exposes Swagger UI; detailed models and docs used.

#### Cloud Run / Hosting
- **Objective**: Run your API server in the cloud.
- **State**: Complete
- **Code Reference**: Deployed and running on PythonAnywhere via the CI workflow.

### Developer Experience

#### Developer Environment
- **Objective**: Group Dev Env Working.
- **State**: Complete
- **Code Reference**: `makefile`, `requirements.txt`, `readme.MD` setup steps.

# Goals for This Semester

## Frontend

- Todo

## Backend Enhancements

- Todo

## Developer Experience

- Todo
