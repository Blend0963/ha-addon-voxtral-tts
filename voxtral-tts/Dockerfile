ARG BUILD_FROM
FROM ${BUILD_FROM}

# Dépendances système
RUN apk add --no-cache \
    python3 \
    py3-pip \
    ffmpeg

# Dépendances Python
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Copie des fichiers de l'addon
COPY rootfs /
COPY run.sh /

RUN chmod a+x /run.sh
