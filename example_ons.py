"""
Exemplo de uso da integração com ONS
Este script demonstra como usar o cliente ONS para obter dados do sistema elétrico brasileiro
"""

from ons_integration import ONSClient
from datetime import datetime, timedelta


def main():
    """Demonstra o uso do cliente ONS"""
    
    print("=" * 60)
    print("Exemplo de Integração com ONS - dados.ons.org.br")
    print("=" * 60)
    print()
    
    # Criar cliente ONS
    client = ONSClient()
    
    # 1. Listar datasets disponíveis
    print("1. Listando datasets disponíveis...")
    print("-" * 60)
    try:
        datasets = client.list_datasets()
        
        if datasets:
            print(f"Encontrados {len(datasets)} datasets:\n")
            for i, dataset in enumerate(datasets, 1):
                name = dataset.get("name", "N/A")
                title = dataset.get("title", "N/A")
                print(f"{i}. {name}")
                print(f"   Título: {title}")
                
                # Mostrar recursos disponíveis
                resources = dataset.get("resources", [])
                if resources:
                    print(f"   Recursos: {len(resources)} arquivo(s)")
                print()
        else:
            print("Nenhum dataset encontrado ou erro ao acessar a API.")
            print("Nota: A API do ONS pode estar temporariamente indisponível.")
    except Exception as e:
        print(f"Erro ao listar datasets: {str(e)}")
    
    print()
    
    # 2. Buscar datasets específicos
    print("2. Buscando datasets relacionados à 'carga'...")
    print("-" * 60)
    try:
        datasets = client.search_datasets("carga")
        
        if datasets:
            print(f"Encontrados {len(datasets)} dataset(s):\n")
            for i, dataset in enumerate(datasets[:5], 1):  # Mostrar apenas os 5 primeiros
                name = dataset.get("name", "N/A")
                title = dataset.get("title", "N/A")
                print(f"{i}. {name}")
                print(f"   Título: {title}")
                print()
        else:
            print("Nenhum dataset encontrado para 'carga'.")
    except Exception as e:
        print(f"Erro ao buscar datasets: {str(e)}")
    
    print()
    
    # 3. Buscar datasets de geração
    print("3. Buscando datasets relacionados à 'geração'...")
    print("-" * 60)
    try:
        datasets = client.search_datasets("geracao")
        
        if datasets:
            print(f"Encontrados {len(datasets)} dataset(s):\n")
            for i, dataset in enumerate(datasets[:5], 1):
                name = dataset.get("name", "N/A")
                title = dataset.get("title", "N/A")
                print(f"{i}. {name}")
                print(f"   Título: {title}")
                print()
        else:
            print("Nenhum dataset encontrado para 'geração'.")
    except Exception as e:
        print(f"Erro ao buscar datasets: {str(e)}")
    
    print()
    
    # 4. Obter informações de um dataset específico
    print("4. Obtendo informações detalhadas de um dataset...")
    print("-" * 60)
    try:
        # Buscar primeiro dataset disponível
        datasets = client.search_datasets("energia")
        
        if datasets and len(datasets) > 0:
            dataset_id = datasets[0].get("id") or datasets[0].get("name")
            
            if dataset_id:
                print(f"Dataset ID: {dataset_id}\n")
                info = client.get_dataset_info(dataset_id)
                
                if info:
                    print(f"Nome: {info.get('name', 'N/A')}")
                    print(f"Título: {info.get('title', 'N/A')}")
                    print(f"Descrição: {info.get('notes', 'N/A')[:200]}...")
                    print(f"Organização: {info.get('organization', {}).get('title', 'N/A')}")
                    
                    resources = info.get("resources", [])
                    if resources:
                        print(f"\nRecursos ({len(resources)}):")
                        for i, resource in enumerate(resources[:3], 1):
                            print(f"  {i}. {resource.get('name', 'N/A')}")
                            print(f"     Formato: {resource.get('format', 'N/A')}")
                            print(f"     URL: {resource.get('url', 'N/A')[:80]}...")
                else:
                    print("Não foi possível obter informações do dataset.")
        else:
            print("Nenhum dataset encontrado.")
    except Exception as e:
        print(f"Erro ao obter informações do dataset: {str(e)}")
    
    print()
    print("=" * 60)
    print("Exemplo concluído!")
    print("=" * 60)
    print()
    print("Nota: Esta integração demonstra como acessar dados do ONS.")
    print("Para análise de ações, você pode usar esses dados para:")
    print("- Correlacionar geração de energia com ações de empresas do setor elétrico")
    print("- Analisar impacto de carga no preço de energia (PLD)")
    print("- Avaliar tendências de fontes renováveis")
    print()


if __name__ == "__main__":
    main()
