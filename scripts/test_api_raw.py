#!/usr/bin/env python3
"""
Script para fazer chamadas diretas à API do PandaScore e exibir respostas em raw JSON.
Testa os endpoints: upcoming, running e finished matches.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import os

load_dotenv()

PANDASCORE_API_KEY = os.getenv("PANDASCORE_API_KEY")
BASE_URL = "https://api.pandascore.co/csgo/matches"

if not PANDASCORE_API_KEY:
    print("❌ ERRO: PANDASCORE_API_KEY não encontrada em .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_API_KEY}",
    "Accept": "application/json"
}


async def fetch_endpoint(session: aiohttp.ClientSession, endpoint: str, params: dict = None) -> dict:
    """Faz uma chamada GET ao endpoint e retorna a resposta em JSON."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"\n📍 Chamando: {url}")
        if params:
            print(f"📦 Parâmetros: {params}")
        
        async with session.get(url, headers=HEADERS, params=params, timeout=10) as response:
            data = await response.json()
            
            print(f"✅ Status: {response.status}")
            print(f"📊 Tamanho da resposta: {len(json.dumps(data))} bytes")
            
            return {
                "status": response.status,
                "url": str(response.url),
                "headers": dict(response.headers),
                "data": data
            }
    
    except asyncio.TimeoutError:
        print(f"❌ TIMEOUT ao chamar {url}")
        return None
    except aiohttp.ClientError as e:
        print(f"❌ ERRO na requisição: {e}")
        return None


async def main():
    """Função principal que executa os testes."""
    print("=" * 80)
    print("🔍 TEST API RAW - PandaScore CS2 Matches")
    print("=" * 80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🔑 API Key: {PANDASCORE_API_KEY[:20]}...")
    print()
    
    async with aiohttp.ClientSession() as session:
        results = {}
        
        # 1. Upcoming matches
        print("\n" + "=" * 80)
        print("1️⃣  UPCOMING MATCHES")
        print("=" * 80)
        results["upcoming"] = await fetch_endpoint(
            session, 
            "/upcoming",
            {"per_page": 10}
        )
        
        # 2. Running matches
        print("\n" + "=" * 80)
        print("2️⃣  RUNNING MATCHES")
        print("=" * 80)
        results["running"] = await fetch_endpoint(
            session,
            "/running",
            {"per_page": 10}
        )
        
        # 3. Finished matches
        print("\n" + "=" * 80)
        print("3️⃣  FINISHED MATCHES")
        print("=" * 80)
        results["finished"] = await fetch_endpoint(
            session,
            "/past",
            {"filter[status]": "finished", "per_page": 10}
        )
        
        # 4. Canceled matches
        print("\n" + "=" * 80)
        print("4️⃣  CANCELED MATCHES")
        print("=" * 80)
        results["canceled"] = await fetch_endpoint(
            session,
            "/past",
            {"filter[status]": "canceled", "per_page": 10}
        )
        
        # Salva os resultados em um arquivo JSON
        output_file = Path(__file__).parent.parent / "data" / "api_raw_responses.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n" + "=" * 80)
        print("✅ RESUMO")
        print("=" * 80)
        print(f"📁 Resultados salvos em: {output_file}")
        print()
        
        for endpoint_name, response in results.items():
            if response and response["status"] == 200:
                data_count = len(response["data"]) if isinstance(response["data"], list) else 1
                print(f"✅ {endpoint_name.upper():20} - {data_count} matches")
            else:
                print(f"❌ {endpoint_name.upper():20} - ERRO")
        
        print()
        print("=" * 80)
        print("📄 EXIBINDO RESPOSTAS EM DETALHES")
        print("=" * 80)
        
        for endpoint_name, response in results.items():
            if response:
                print(f"\n\n{'#' * 80}")
                print(f"### {endpoint_name.upper()}")
                print(f"{'#' * 80}")
                print(json.dumps(response, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    print("\n🚀 Iniciando testes de API...\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n\n✅ Teste concluído com sucesso!")
