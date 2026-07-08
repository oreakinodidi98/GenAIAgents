FROM python:3.13-slim AS builder

WORKDIR /app/user_agent

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --no-create-home appuser

# # Create non-root user for runtime
# RUN groupadd --gid 1000 appuser \
#     && useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin appuser

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . user_agent/

WORKDIR /app/user_agent

# Ensure the runtime user can read and execute the app files
# RUN chown -R appuser:appuser /app/user_agent

# Switch to non-root user
USER appuser

EXPOSE 8088

CMD ["python", "main.py"]