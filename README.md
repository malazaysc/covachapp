# CovachApp

CovachApp is a Django + HTMX + Tailwind hospitality marketplace where approved hosts can list rental properties and guests can search and request reservations.

## Stack

- Django monolith with server-rendered templates and HTMX partial updates
- Tailwind CSS styling
- PostgreSQL + PostGIS
- OpenStreetMap + Leaflet maps
- S3-compatible media storage via `django-storages`

## Features in this version

- Email/password signup with verification email flow
- Host application and admin approval workflow
- Listing CRUD for approved hosts with cancellation policy and availability blocks
- Search with filters, date availability checks, and OSM map pins
- Request-to-book reservation flow with host approval/decline
- Reservation event audit history
- In-app notification inbox plus transactional email notifications
- Custom `/ops` portal for host/listing/reservation moderation and metrics

## Quick Start

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

To include Mailpit for SMTP capture:

```bash
docker compose --profile mail up --build
```

3. Open app:

- App: [http://localhost:8000](http://localhost:8000)
- Mailpit UI (if `mail` profile is enabled): [http://localhost:8025](http://localhost:8025)

4. Optional demo seed:

```bash
docker compose exec web python manage.py seed_demo_data
```

By default, the container entrypoint auto-runs:

```bash
python manage.py seed_demo_data --if-empty
```

right after migrations, so first boot gets demo data and later restarts skip duplicates.
Set `AUTO_SEED_DEMO=0` in `.env` to disable.

## Key URLs

- `/` home
- `/search/` results + map
- `/listings/<slug>/` listing detail
- `/reservations/request/` create reservation request
- `/host/dashboard` host dashboard
- `/host/listings` host listings
- `/host/reservations` host reservation management
- `/guest/trips` guest trip history
- `/guest/inbox` in-app messages
- `/ops/` custom ops portal

## Background Tasks

Expire stale booking requests (24h SLA):

```bash
docker compose exec web python manage.py expire_reservation_requests
```

Run this daily via cron or your scheduler.

## Testing

```bash
docker compose run --rm web python -m pytest
```

## Notes

- Default database backend is PostGIS (`DB_ENGINE=django.contrib.gis.db.backends.postgis`).
- For non-spatial local tooling, you can temporarily set `DB_ENGINE=django.db.backends.postgresql`.
