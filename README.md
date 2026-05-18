# Red de Honeypots Distribuida con T-Pot

Arquitectura Hive + Sensor sobre infraestructura doméstica

Proyecto de fin de ciclo CFGS ASIR — IES Gaspar Melchor de Jovellanos  
Autores: Adrián Pérez Peláez, Víctor Manuel Humanes Ruiz, Izan Lozano Hernández  
Tutor: Javier Ortiz Laguna  
Mayo 2026

---

## Qué es esto

Este repositorio recoge todo el trabajo realizado para montar una red de honeypots distribuida usando T-Pot. Dos servidores físicos, uno en Toledo y otro en Madrid, ambos expuestos a internet y capturando ataques reales. El Nodo 1 actúa como Hive (centraliza todo) y el Nodo 2 como Sensor (manda los logs al Hive). Todo va cifrado por Tailscale y tenemos un bot de Telegram que avisa cuando hay movimiento.

Lo hicimos sobre infraestructura doméstica real, no en un laboratorio de clase. Por eso nos encontramos con problemas de verdad: routers de operador con funciones limitadas, doble NAT por un extensor WiFi, certificados SSL que no funcionaban como esperábamos... cosas que no te salen en un entorno controlado.

---

## Estructura del repositorio

| Carpeta | Qué hay dentro |
|---------|----------------|
| `docs/` | Memoria del proyecto en PDF y DOCX, y la presentación final |
| `src/telegram-bot/` | Código Python del bot de alertas + fichero de servicio systemd |
| `config/` | Configuraciones aplicadas en cada nodo: reglas UFW, Fail2ban, fix de Logstash |
| `infra/` | Diagrama de arquitectura, tabla de hardware/software, fotos de los servidores |
| `screenshots/` | Capturas del dashboard de Kibana, alertas de Telegram, panel de Tailscale, contenedores Docker |
| `videos/` | Vídeos de demostración: acceso al sistema y ataque simulado |

---

## Cómo navegar este repo

Si eres profesor y estás corrigiendo:

1. **Empieza por `docs/Memoria_Final_VIA.pdf`** — ahí está todo documentado: planificación, semanas de trabajo, problemas, soluciones y resultados.
2. **Luego mira `docs/Presentacion_TPot.pdf`** — la presentación que usamos para la defensa del proyecto.
3. **Si te interesa el código**, entra en `src/telegram-bot/` — el script está comentado y tiene las variables configurables al inicio.
4. **Para ver cómo quedó montado**, revisa `infra/diagrama-arquitectura.png` y las capturas en `screenshots/`.

---

## Arquitectura resumida

```
[Adrián] ─────┐
[Víctor] ─────┼──► Tailscale VPN ──► Internet
[Izan] ───────┘         │
                        │
              ┌─────────┴─────────┐
              │                   │
        [Router ADAMO]      [Router Zyxel Digi]
              │                   │
              ▼                   ▼
        Nodo 1 (Hive)      Nodo 2 (Sensor)
        Casa Víctor         Casa Izan
        Toledo              Madrid
        • 40 honeypots      • Honeypots + Logstash
        • ELK Stack         • Reenvía logs al Hive
        • Suricata          • Todo cifrado por Tailscale
        • Bot Telegram
        • Debian 11 + Docker
```

---

## Tecnologías utilizadas

- **T-Pot CE** — telekom-security/tpotce (repositorio oficial)
- **Debian 11 Bullseye** — sin escritorio en ambos nodos
- **Docker 29.4.0** + Docker Compose v5.1.1
- **Tailscale** — VPN mesh para acceso remoto y túnel entre nodos
- **Elasticsearch, Logstash, Kibana** — pila ELK incluida en T-Pot
- **Python 3** — bot de alertas Telegram
- **UFW + Fail2ban** — firewall y protección contra fuerza bruta
- **DuckDNS** — DNS dinámico gratuito

---

## El bot de Telegram

Está en `src/telegram-bot/honeypot_alertas.py`. Monitoriza los logs del kernel donde UFW registra conexiones, detecta IPs nuevas, las geolocaliza con ipinfo.io y manda resúmenes al grupo del equipo.

Configuración actual:
- Avisa cada **40 IPs nuevas** o cada **60 minutos**, lo que pase primero
- Variables tocables al inicio del script: `LIMITE_ALERTAS` e `INTERVALO_MAXIMO`
- Corre como servicio systemd (`honeypot-alertas.service`) para arrancar solo con el servidor

La base del código la generamos con ChatGPT, pero lo revisamos, adaptamos y pusimos a funcionar nosotros. No somos programadores, somos administradores de sistemas.

---

## Problemas que tuvimos y cómo los solucionamos

| Problema | Solución |
|----------|----------|
| Fork de T-Pot de 2020 con 600+ commits de retraso | Migrar al repositorio oficial de Telekom Security |
| PC inicial con 8 GB RAM (mínimo justo para T-Pot) | Sustituir por servidor con 11 GB RAM |
| Conflicto GPG entre docker.asc y docker.gpg | Eliminar ficheros en conflicto y relanzar instalador |
| Puerto 25 ocupado por exim4 en Debian | `systemctl stop exim4 && systemctl disable exim4` |
| Doble NAT por extensor WiFi en Nodo 2 | Configurar ruta y DNS manualmente en el servidor |
| Certificado SSL del Hive no incluía IP Tailscale | Desactivar verificación SSL en Logstash: `LS_SSL_VERIFICATION=none` |
| DNS y ruta por defecto no persistentes en Nodo 2 | Configurar manualmente en `/etc/resolv.conf` y rutas estáticas |

Todo esto está explicado con más detalle en la memoria.

---

## Resultados

- Más de **1.500 eventos capturados** en el Nodo 2 durante el período de exposición
- Ambos nodos reciben ataques de forma simultánea desde IPs públicas independientes
- Dashboard de Kibana accesible vía Tailscale con mapa de ataques en tiempo real
- Bot de Telegram enviando alertas periódicas al grupo del equipo

---

## Créditos

- **Adrián Pérez Peláez** — Introducción, bot de Telegram, memoria y presentación
- **Víctor Manuel Humanes Ruiz** — Nodo 1 (Hive), hardware, instalación T-Pot, seguridad perimetral
- **Izan Lozano Hernández** — Nodo 2 (Sensor), integración con Hive, resolución de problemas de red
- **Javier Ortiz Laguna** — Tutor del proyecto

Proyecto realizado en el **IES Gaspar Melchor de Jovellanos**, Fuenlabrada.  
Ciclo Formativo de Grado Superior en **Administración de Sistemas Informáticos en Red (ASIR)**.  
Promoción 2025-2026.

---

## Licencia

Este proyecto es trabajo académico. El código del bot está disponible para consulta y aprendizaje.  
Las capturas de pantalla y datos de ataques son reales obtenidos durante el período de exposición del honeypot.
