FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Instalar Google Chrome con versión específica
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome-keyring.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/google-chrome-keyring.gpg arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Crear usuario no-root con UID específico
RUN groupadd -r scraper && useradd -r -g scraper -u 1001 -d /app scraper

WORKDIR /app

# Copiar archivos con permisos correctos
COPY --chown=scraper:scraper . .

# Dar permisos necesarios para Chrome sandboxing
RUN chmod 755 /app && \
    mkdir -p /app/.config && \
    chown -R scraper:scraper /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Cambiar a usuario no-root
USER scraper

# Verificar que Chrome está accesible
RUN /usr/bin/google-chrome --version

# Ejecutar el scraper
CMD ["python", "main.py"]
