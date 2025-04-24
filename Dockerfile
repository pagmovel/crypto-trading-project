FROM python:3.9-slim

WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt setup.py ./

# Instala as dependências Python
RUN pip install --no-cache-dir -e .

# Copia o resto do código
COPY . .

# Expõe a porta do dashboard
EXPOSE 8050

# Comando para iniciar o dashboard
CMD ["python", "examples/dashboard_example.py"]