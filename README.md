# stockanalisys
analisar uma ação e verificar dados que podem influenciar ela.

## Integração com ONS

Este projeto inclui integração com o portal de dados do ONS (Operador Nacional do Sistema Elétrico) disponível em https://dados.ons.org.br/

### Funcionalidades

A integração permite acessar dados do sistema elétrico brasileiro, incluindo:
- Listagem de datasets disponíveis
- Busca de datasets por termos específicos
- Obtenção de informações detalhadas de datasets
- Acesso a dados de carga do sistema
- Acesso a dados de geração por fonte de energia

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ppaulojr/stockanalisys.git
cd stockanalisys
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Uso

#### Exemplo básico

```python
from ons_integration import ONSClient

# Criar cliente
client = ONSClient()

# Listar datasets disponíveis
datasets = client.list_datasets()
for dataset in datasets:
    print(f"Dataset: {dataset['name']}")
    print(f"Título: {dataset['title']}")

# Buscar datasets específicos
datasets_carga = client.search_datasets("carga")
for dataset in datasets_carga:
    print(f"Dataset de carga: {dataset['title']}")

# Obter informações de um dataset
info = client.get_dataset_info("dataset-id")
if info:
    print(f"Descrição: {info['notes']}")
```

#### Executar exemplo completo

```bash
python example_ons.py
```

### Estrutura do Projeto

```
stockanalisys/
├── ons_integration/         # Módulo de integração com ONS
│   ├── __init__.py         # Exportações do módulo
│   ├── client.py           # Cliente da API do ONS
│   └── models.py           # Modelos de dados
├── example_ons.py          # Exemplo de uso
├── requirements.txt        # Dependências do projeto
└── README.md              # Este arquivo
```

### Como usar para análise de ações

Os dados do ONS podem ser úteis para análise de ações do setor elétrico:

1. **Geração de Energia**: Correlacionar dados de geração com performance de empresas geradoras
2. **Carga do Sistema**: Analisar demanda de energia e seu impacto no PLD (Preço de Liquidação das Diferenças)
3. **Fontes Renováveis**: Avaliar tendências de geração eólica e solar
4. **Hidrologia**: Dados de reservatórios podem impactar empresas hidrelétricas

### API do ONS

A API do ONS utiliza o padrão CKAN e oferece os seguintes endpoints principais:

- `package_list`: Lista todos os datasets
- `package_show`: Detalhes de um dataset específico
- `package_search`: Busca datasets por termo
- `datastore_search`: Busca dados dentro de um recurso

Para mais informações sobre a API: https://dados.ons.org.br/

### Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

### Licença

Este projeto está sob a licença especificada no arquivo LICENSE.
