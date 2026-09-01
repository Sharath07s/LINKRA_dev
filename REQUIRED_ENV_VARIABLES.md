# Required Environment Variables

This document outlines the environment variables required to run the KCIA (Karnataka Crime Intelligence Application) locally and in production.

## Mandatory Environment Variables

These variables **must** be configured for the application to function correctly.

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| `SECRET_KEY` | Used for cryptographic signing (JWT tokens, etc.). Must be changed in production. | `change-me-to-a-very-long-random-secret-key-in-production` (Use a strong random string like `openssl rand -hex 32`) |
| `AI_PROVIDER` | Determines which AI service the application will use. | `openai`, `gemini`, `anthropic`, or `deepseek` |
| `*_API_KEY` | You must provide the API key corresponding to your chosen `AI_PROVIDER`. | e.g. `OPENAI_API_KEY=sk-...` |

### Required Database & Service Configs
*Note: You must define these variables in your `.env` file even for local development.*

| Variable | Description | Default Local Value |
| :--- | :--- | :--- |
| `POSTGRES_SERVER` | Hostname of the PostgreSQL database. | `localhost` |
| `POSTGRES_PORT` | Port of the PostgreSQL database. | `5432` |
| `POSTGRES_USER` | PostgreSQL user. | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password. | (must provide) |
| `POSTGRES_DB` | PostgreSQL database name. | `sih26189_db` |
| `REDIS_URL` | Connection URL for Redis. | `redis://localhost:6379/0` |
| `NEO4J_URI` | Connection URI for Neo4j. | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username. | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password. | (must provide) |
| `NEXT_PUBLIC_API_URL` | API URL for the frontend. | `http://localhost:8000/api/v1` |

## Optional Environment Variables

These variables have sensible defaults or are only needed for specific configurations.

| Variable | Description | Example/Default Value |
| :--- | :--- | :--- |
| `APP_NAME` | The name of the application. | `KCIA` |
| `APP_ENV` | The environment the app is running in (`development`, `staging`, `production`). | `development` |
| `DEBUG` | Enables debug mode. | `True` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Expiration time for JWT access tokens. | `30` |
| `API_V1_STR` | Prefix for the V1 API routes. | `/api/v1` |
| Unused API Keys | API keys for providers not selected in `AI_PROVIDER`. | (Leave blank or omit) |
