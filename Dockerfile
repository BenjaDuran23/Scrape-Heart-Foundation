FROM python:3.11-slim

# Solo lo estrictamente necesario (menor superficie de ataque)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Google Chrome desde el canal estable oficial, con repo firmado por keyring y sobre HTTPS
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome-keyring.gpg && \
    chmod 0644 /etc/apt/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Chromedriver fijado a la MISMA versión de Chrome estable ya instalada.
# Se resuelve en build time: en runtime no hay descargas ni Selenium Manager.
RUN set -eux; \
    CHROME_VERSION="$(google-chrome --version | awk '{print $3}')"; \
    if ! curl -fsSL -o /tmp/chromedriver.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip"; then \
        CHROME_VERSION="$(curl -fsSL https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE)"; \
        curl -fsSL -o /tmp/chromedriver.zip \
            "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip"; \
    fi; \
    unzip -j /tmp/chromedriver.zip 'chromedriver-linux64/chromedriver' -d /usr/local/bin; \
    rm -f /tmp/chromedriver.zip; \
    chmod 0755 /usr/local/bin/chromedriver; \
    google-chrome --version; \
    chromedriver --version

ENV CHROMEDRIVER=/usr/local/bin/chromedriver

# Usuario sin privilegios con HOME propio y escribible.
# HOME NO es /app: /app se monta desde el host y dejaría a Chrome sin dónde escribir.
RUN groupadd -g 1001 scraper && \
    useradd -m -u 1001 -g scraper -d /home/scraper -s /usr/sbin/nologin scraper
ENV HOME=/home/scraper

WORKDIR /app

# Crear virtual environment como root
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Dependencias antes que el código: mejor cache de capas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verificación en BUILD TIME: si una dependencia no queda instalada donde el
# intérprete la busca, el build falla acá y no con un ModuleNotFoundError en runtime.
RUN python -c "import selenium, bs4, requests; print('deps OK', selenium.__version__)"

COPY *.py ./

# Mínimo privilegio: el venv y el driver quedan solo-lectura para quien ejecuta.
# Solo /app queda escribible, porque ahí se genera data.json.
RUN chmod -R a=rX /opt/venv && \
    chown -R scraper:scraper /app

# Cambiar a usuario no-root
USER scraper

# El usuario sin privilegios debe ver el venv y el driver
RUN python -c "import selenium" && chromedriver --version

# Ejecutar el scraper
CMD ["python", "main.py"]
