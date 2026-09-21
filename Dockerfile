# Root Dockerfile so the repo deploys directly from GitHub (InstaCloud connect-repo,
# Railway/Render-style UIs, or any agent that expects ./Dockerfile).
# Same recipe as deploy/Dockerfile.
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir fastapi uvicorn
COPY . /app/src
RUN pip install --no-cache-dir /app/src
RUN python -c "import laya; laya.load('convaiinnovations/laya', subfolder='typed-decisions'); print('weights cached')"
COPY deploy/app.py .
ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
