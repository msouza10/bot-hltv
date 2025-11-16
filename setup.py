#!/usr/bin/env python3
"""
Script de inicialização rápida do bot.
Cria o ambiente virtual e instala dependências se necessário.
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Executa um comando shell e reporta o resultado."""
    print(f"⚙️  {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✓ {description} - OK\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro: {e}\n")
        return False


def check_env_file():
    """Verifica se o arquivo .env existe."""
    if not os.path.exists(".env"):
        print("⚠️  Arquivo .env não encontrado!")
        print("   Copie .env.example para .env e configure os tokens:")
        print("   cp .env.example .env\n")
        return False
    return True


def main():
    """Função principal."""
    print("=" * 60)
    print("🚀 Bot HLTV - Script de Inicialização")
    print("=" * 60)
    print()
    
    # Verificar Python
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detectado\n")
    
    # Verificar .env
    if not check_env_file():
        sys.exit(1)
    
    # Verificar/criar venv
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Criando ambiente virtual"):
            sys.exit(1)
    else:
        print("✓ Ambiente virtual já existe\n")
    
    # Determinar comando de ativação
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Instalar/atualizar dependências
    if not run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Instalando dependências"
    ):
        sys.exit(1)
    
    print("=" * 60)
    print("✅ Setup concluído com sucesso!")
    print("=" * 60)
    print()
    print("Para iniciar o bot, execute:")
    print(f"  {activate_cmd}")
    print(f"  python -m src.bot")
    print()
    print("Ou use o atalho:")
    print(f"  {python_cmd} -m src.bot")
    print()


if __name__ == "__main__":
    main()
