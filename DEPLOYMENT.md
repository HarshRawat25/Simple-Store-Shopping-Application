# Production deployment

This project is ready for a standard Django host that provides HTTPS and a PostgreSQL database.

## Required environment variables

Set these as private environment variables in your hosting dashboard:

```text
DJANGO_ENV=production
DJANGO_SECRET_KEY=<a long random secret>
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

Do not set `DJANGO_DEBUG=True` in production.

The production configuration enables HSTS for the main domain and all
subdomains. Only deploy it to domains where every subdomain is served over HTTPS.

## Build and start commands

Use the following build command:

```text
bash build.sh
```

Use the following start command:

```text
gunicorn ecommerce_project.wsgi:application
```

## Media files

The product images currently live in `media/`. In production, attach persistent disk storage or configure object storage before accepting user uploads. Ephemeral hosting filesystems can lose uploaded media after a redeploy.

## Final deployment check

After configuring the production variables and installing dependencies, run:

```text
python manage.py check --deploy
```
