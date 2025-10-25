FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    binwalk \
    foremost \
    exiftool \
    file \
    pngcheck \
    libmagic1 \
    ruby \
    ruby-dev \
    steghide \
    wget \
    && rm -r /var/lib/apt/lists/*

RUN gem install zsteg

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install stegoveritas && \
    stegoveritas_install_deps || true

COPY app.py .
COPY templates/ ./templates/

RUN mkdir -p uploads output

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python3", "app.py"]

