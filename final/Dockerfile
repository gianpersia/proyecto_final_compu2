#imagen python
FROM python:3.10-slim

#directorio de trabajo dentro del contenedor
WORKDIR /app

COPY requirements.txt .
#instalar dependencias, con --no-cache-dir no guarda los archivos temporales grandes
RUN pip install --no-cache-dir -r requirements.txt

#copiar todos los archivos del proyecto al contenedor
COPY ./src /app

#expongo el puerto 8080 (el que usa el server)
EXPOSE 8080

#comando por defecto al iniciar el contenedor
CMD ["python", "server_asyncio.py"]