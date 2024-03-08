# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

# * Docker İmajı
FROM python:3.11.6-slim-bookworm

# * Python Standart Değişkenler
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING="UTF-8"

# * Çalışma Alanı
WORKDIR /usr/src/keenetic_exporter
COPY ./ /usr/src/keenetic_exporter

# ? Sistem Kurulumları
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
        git \
        locales && \
    sed -i -e 's/# tr_TR.UTF-8 UTF-8/tr_TR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

# * Dil ve Bölge
ENV LANGUAGE="tr_TR.UTF-8" LANG="tr_TR.UTF-8" LC_ALL="tr_TRC.UTF-8" TZ="Europe/Istanbul"

# ? Gereksiz Dosyaların Silinmesi
RUN rm -rf /var/lib/apt/lists/*

# * Gerekli Paketlerin Yüklenmesi
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir -U setuptools wheel && \
    python3 -m pip install --no-cache-dir -Ur requirements.txt

# * Python Çalıştırılması
CMD ["python3", "start.py"]