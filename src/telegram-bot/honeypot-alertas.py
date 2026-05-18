#!/usr/bin/env python3

import re
import ipinfo
import requests
import time
from datetime import datetime
from collections import Counter

# =====================================================================
# CONFIGURACIÓN — Rellena estas variables con tus datos reales
# =====================================================================
TELEGRAM_TOKEN = "TU_TELEGRAM_BOT_TOKEN_AQUI"
CHAT_ID = "TU_CHAT_ID_AQUI"
IPINFO_TOKEN = "TU_TOKEN_IPINFO_AQUI"
# =====================================================================

LIMITE_ALERTAS = 40
INTERVALO_MAXIMO = 3600

LOG_FILE = "/home/via/tpotce/data/honeytrap/log/honeytrap.log"

handler = ipinfo.getHandler(IPINFO_TOKEN)


def enviar(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}, timeout=10)


def get_pais(ip):
    try:
        details = handler.getDetails(ip)
        return getattr(details, 'country_name', 'Desconocido')
    except:
        return 'Desconocido'


def enviar_resumen(nuevas):
    paises = Counter()
    for ip in nuevas:
        paises[get_pais(ip)] += 1
    top5 = paises.most_common(5)
    top_str = "\n".join([f"🏴 {p}: {c} ataques" for p, c in top5])
    mensaje = (
        f"📊 <b>Resumen de ataques — LocalHoneypot</b>\n\n"
        f"🕐 Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"🌐 IPs nuevas detectadas: {len(nuevas)}\n\n"
        f"🏆 Top 5 países atacantes:\n{top_str}"
    )
    enviar(mensaje)
    print(f"Resumen enviado: {len(nuevas)} IPs")


enviar("✅ <b>LocalHoneypot activo</b>\nBot iniciado correctamente.")

# Posicionarse al final del fichero
with open(LOG_FILE, 'r') as f:
    f.seek(0, 2)
    posicion = f.tell()

print(f"Monitorizando desde el final del log...")
nuevas_acumuladas = set()
ultimo_envio = time.time()

while True:
    time.sleep(60)
    with open(LOG_FILE, 'r') as f:
        f.seek(posicion)
        lineas_nuevas = f.read()
        posicion = f.tell()

    ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+', lineas_nuevas)
    nuevas = {ip for ip in ips if ip and not ip.startswith('192.168') and not
              ip.startswith('10.') and not ip.startswith('100.')}
    nuevas_acumuladas.update(nuevas)
    print(f"IPs nuevas este minuto: {len(nuevas)} | Acumuladas: {len(nuevas_acumuladas)}")

    tiempo = time.time() - ultimo_envio
    if len(nuevas_acumuladas) >= LIMITE_ALERTAS or tiempo >= INTERVALO_MAXIMO:
        if nuevas_acumuladas:
            enviar_resumen(nuevas_acumuladas)
            nuevas_acumuladas = set()
            ultimo_envio = time.time()
