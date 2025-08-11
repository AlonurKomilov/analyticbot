# =================================================================
# 1-BOSQICH: "Builder" - Bog'liqliklarni o'rnatish uchun
# =================================================================
# Biz yengil python:3.11-slim obrazidan boshlaymiz va unga "builder" deb nom beramiz
FROM python:3.11-slim as builder

# Ishchi papkani o'rnatamiz
WORKDIR /app

# Poetry o'rnatuvchisini o'rnatamiz, bu bog'liqliklarni boshqarish uchun kerak
RUN pip install poetry

# Virtual muhit yaratishni o'chirib qo'yamiz
RUN poetry config virtualenvs.create false

# Bog'liqliklar fayllarini nusxalaymiz
COPY poetry.lock pyproject.toml ./

# === MUHIM O'ZGARISH MANA SHU YERDA ===
# Bog'liqliklarni o'rnatamiz. --only main faqat production uchun kerakli kutubxonalarni o'rnatadi.
# Bu eski --no-dev komandasining yangi ko'rinishi.
RUN poetry install --only main --no-root


# =================================================================
# 2-BOSQICH: "Final" - Yakuniy, yengil obrazni yaratish
# =================================================================
# Yana o'sha toza va yengil python:3.11-slim obrazidan boshlaymiz
FROM python:3.11-slim

# Ishchi papkani o'rnatamiz
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Also copy the executables
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Konteyner ishga tushganda bajariladigan komanda
CMD ["python", "run_bot.py"]
