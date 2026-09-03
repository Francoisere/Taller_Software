FROM mcr.microsoft.com/playwright/python:v1.48.0-noble

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Asegurar instalación de Playwright y dependencias de sistema
RUN playwright install chromium

# Copiar código del proyecto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
