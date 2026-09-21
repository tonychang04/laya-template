# Build from the repository root:
#   docker build -f deploy/Dockerfile -t laya-api .
# Run:
#   docker run -p 8080:8080 laya-api
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir fastapi uvicorn
COPY . /app/src
RUN pip install --no-cache-dir /app/src
# Bake the typed-decisions checkpoint into the image
RUN python -c "import laya; laya.load('convaiinnovations/laya', subfolder='typed-decisions'); print('weights cached')"
COPY deploy/app.py .
ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
