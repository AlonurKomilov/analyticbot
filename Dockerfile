# 1-qism: Bog'liqliklarni o'rnatish uchun "builder"
# Bu qism faqat kutubxonalarni o'rnatish uchun ishlatiladi va oxirgi image'ga kirmaydi.
# Bu image hajmini kichik saqlashga yordam beradi.
FROM python:3.11-slim AS builder

# Tizimga kerakli paketlarni o'rnatamiz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev

# Ishchi papkani yaratamiz
WORKDIR /app

# Poetry o'rnatamiz
RUN pip install poetry

# Poetry'ga virtual muhit yaratmaslikni buyuramiz
RUN poetry config virtualenvs.create false

# Bog'liqliklar fayllarini nusxalaymiz
COPY poetry.lock pyproject.toml ./

# Bog'liqliklarni o'rnatamiz. --only main faqat production uchun kerakli kutubxonalarni o'rnatadi.
# Bu eski --no-dev komandasining yangi ko'rinishi.
RUN poetry install --only main --no-root


# 2-qism: Development uchun
FROM builder AS development

RUN poetry install


# 3-qism: Production uchun optimallashtirilgan "final" image
# Bu yerdan boshlab oxirgi, ishchi image'lar yasaladi
FROM python:3.11-slim AS final

WORKDIR /app

# O'rnatilgan kutubxonalarni "builder"dan nusxalaymiz
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Loyiha fayllarini nusxalaymiz
COPY . .


# 4-qism: Har bir servis uchun alohida ishga tushirish buyruqlari

# BOTTING O'ZI UCHUN BOSQICH
FROM final AS bot
CMD ["python", "run_bot.py"]

# API UCHUN BOSQICH
FROM final AS api
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# CELERY WORKER UCHUN BOSQICH
FROM final AS celery_worker
CMD ["celery", "-A", "bot.celery_app", "worker", "--loglevel=info"]

# CELERY BEAT UCHUN BOSQICH
FROM final AS celery_beat
CMD ["celery", "-A", "