# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Verificar se requirements.txt existe
RUN if [ ! -f requirements.txt ]; then echo "❌ requirements.txt não encontrado!"; exit 1; fi

# Copiar requirements PRIMEIRO
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO o código
COPY . .

# Verificar estrutura
RUN echo "📁 Estrutura do projeto:" && find . -name "*.py" | head -10

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Comando de inicialização - AJUSTADO para estrutura correta
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
