# Imagen base — Python 3.11 slim es más liviana que la versión completa
# slim no incluye herramientas de compilación innecesarias en producción
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos requirements primero — aprovechamos el cache de Docker
# Si el código cambia pero requirements no, Docker no reinstala dependencias
COPY requirements.txt .

# Instalamos dependencias
# --no-cache-dir reduce el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Puerto que expone el contenedor
EXPOSE 8000

# Comando que corre cuando el contenedor arranca
# --host 0.0.0.0 es necesario para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]