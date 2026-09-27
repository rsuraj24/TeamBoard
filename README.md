# TeamBoard API

TeamBoard is a Django REST API for registering B2B clients, searching a curated knowledge base, and reporting query usage.

## Setup

1. Create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set a strong `DJANGO_SECRET_KEY` and database credentials.

3. Start PostgreSQL:

   ```powershell
   docker compose up -d db
   ```

4. Apply migrations and seed the knowledge base:

   ```powershell
   python manage.py migrate
   python manage.py seed_kb
   ```

5. Start the server:

   ```powershell
   python manage.py runserver
   ```

## Endpoints

- `POST /api/auth/register/` creates a client and returns a JWT access token and generated API key.
- `POST /api/auth/login/` returns a fresh JWT and company credentials.
- `POST /api/kb/query/` searches question and answer text. Send `Authorization: Bearer <access>`.
- `GET /api/admin/usage-summary/` returns usage totals for users whose Company role is `admin`.

The Postman collection is at `postman/TeamBoard.postman_collection.json`. Register/login first, set the `access_token` collection variable, and promote a test company to `admin` through Django admin or the database before testing the admin request.

## Tests

The normal application database is PostgreSQL. The test suite can run without Docker using SQLite:

```powershell
$env:DJANGO_TESTING = '1'
python manage.py test
```