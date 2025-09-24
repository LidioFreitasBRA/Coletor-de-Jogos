#!/usr/bin/env python3
# fix_structure.py
import os
import shutil
from pathlib import Path

def fix_project_structure():
    print("🔧 Corrigindo estrutura do projeto...")
    
    # Criar pasta app se não existir
    if not os.path.exists("app"):
        os.makedirs("app")
        print("✅ Criada pasta app/")
    
    # Mover main.py para o local correto
    if os.path.exists("app/api/core/main.py"):
        # Criar diretório de destino
        os.makedirs("app", exist_ok=True)
        # Mover arquivo
        shutil.move("app/api/core/main.py", "app/main.py")
        # Remover diretórios vazios
        try:
            os.removedirs("app/api/core")
            os.removedirs("app/api")
        except:
            pass
        print("✅ main.py movido para app/main.py")
    
    # Corrigir estrutura da pasta analysts
    if os.path.exists("analysts/__init__.py/score_analyzer.py"):
        # Criar analysts corretamente
        os.makedirs("app/analysts", exist_ok=True)
        
        # Mover arquivos se existirem
        analysts_files = [
            "analysts/__init__.py/score_analyzer.py",
            "analysts/__init__.py/score_report_generator.py"
        ]
        
        for file_path in analysts_files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                shutil.move(file_path, f"app/analysts/{filename}")
                print(f"✅ {filename} movido para app/analysts/")
        
        # Remover estrutura incorreta
        try:
            shutil.rmtree("analysts")
        except:
            pass
    
    # Mover tools para dentro de app/
    if os.path.exists("tools"):
        if not os.path.exists("app/tools"):
            shutil.move("tools", "app/tools")
            print("✅ Pasta tools movida para app/tools/")
    
    # Criar __init__.py necessários
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py", 
        "app/core/__init__.py",
        "app/analysts/__init__.py",
        "app/tools/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Package initialization\n")
            print(f"✅ Criado {init_file}")
    
    print("🎉 Estrutura corrigida com sucesso!")

def create_missing_files():
    """Criar arquivos faltantes"""
    
    # Se main.py não existe, criar
    if not os.path.exists("app/main.py"):
        with open("app/main.py", "w") as f:
            f.write('''from fastapi import FastAPI

app = FastAPI(title="Football Stats API")

@app.get("/")
async def root():
    return {"message": "API funcionando!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
        print("✅ app/main.py criado")
    
    # Se requirements.txt não existe, criar
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write('''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
aiohttp==3.9.1
pandas==2.1.3
numpy==1.24.3
''')
        print("✅ requirements.txt criado")

if __name__ == "__main__":
    fix_project_structure()
    create_missing_files()
    
    # Mostrar estrutura final
    print("\n📁 Estrutura final:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if not file.startswith(".") and not file.startswith("__"):
                print(f"{subindent}{file}")
