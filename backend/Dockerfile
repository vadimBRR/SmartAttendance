#vybrat zakladny obreaz
FROM python:3.13-slim
#nainstalovat chzbajuce balicky/softver
RUN pip install apprise loguru paho-mqtt pydantic pydantic-settings python-dotenv
#prekopirujeme nas projekt4
COPY src/ /app
#povieme co spustit pri spusteni kontejnera
WORKDIR /app
CMD [ "/usr/bin/env", "python3", "main.py" ]