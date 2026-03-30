FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --no-create-home appuser

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY hostedagent.py ./

# Switch to non-root user
USER appuser

EXPOSE 8088

ENV PYTHONUNBUFFERED=1

CMD ["python", "hostedagent.py"]
