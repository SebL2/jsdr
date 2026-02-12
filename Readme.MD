# Flask Geographic API

A comprehensive Flask REST API server for managing geographic data with cities, states, and population information. This project demonstrates modern web development practices including automated testing, CI/CD deployment, and cloud hosting.

## Features

- **RESTful API**: Full CRUD operations for cities and geographic data
- **MongoDB Integration**: Local and cloud database support with caching
- **Automated Testing**: Comprehensive test coverage with pytest
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Cloud Deployment**: Hosted on PythonAnywhere with automatic updates
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Security**: Access control and authentication systems
- **Form Handling**: Web form utilities and validation

## Quick Start

### For Production
```bash
make prod
```

### For Development Environment
```bash
make dev_env
```

### Running Tests
```bash
make all_tests
```

### Linting
```bash
make lint
```

## API Endpoints

The API provides endpoints for:
- Cities management (`/cities`)
- States data (`/states`) 
- Population queries and analytics
- Health checks and system status

Visit `/` when running the server to access the interactive Swagger documentation.

## Project Structure

- `server/` - Flask application and API endpoints
- `cities/` - Cities business logic and data models
- `states/` - States management functionality
- `data/` - Database connection and data access layer
- `security/` - Authentication and access control
- `examples/` - Form handling and utility examples
- `tests/` - Comprehensive test suites for all modules

## Development

This project uses:
- **Flask** with Flask-RESTX for API development
- **MongoDB** for data persistence with caching
- **pytest** for testing framework
- **flake8** for code linting
- **GitHub Actions** for CI/CD

## Development Checklist

- Install MongoDB locally (or run `docker-compose up mongo`).
- Seed data via `python load_geo_script.py` (it will reuse cached JSON if present).
- Run `make dev_env` to install dependencies and `make all_tests` to verify coverage.
- Visit `/` (Swagger UI) after starting the server to explore every documented endpoint.

## Documentation

- [Progress and Goals](ProgressAndGoals.md) - Detailed project status and roadmap
- [MongoDB Installation Guide](docs/InstallingMongoDBOnWSL.md) - Setup instructions

## Group Members

- Sebastian Liu
- Derek Kim  
- Soohyeuk Choi
- Jefferson Le
- Rafiul H. Kashfi
