# Projeto: RagFinal  

## Descrição  
Este projeto é uma Azure Function App que utiliza abordagens de Recuperação e Geração (RAG) para criar soluções baseadas em inteligência artificial no Azure. O objetivo é integrar técnicas de recuperação de informações com modelos generativos para fornecer respostas precisas e contextualizadas.  

## Estrutura do Projeto  
- **Documentação**: Contém informações detalhadas sobre o projeto e como utilizá-lo.  
- **Código**: Scripts e funções para implementação das soluções RAG.  
- **Configuração**: Arquivos de configuração para integração com serviços do Azure.  

## Pré-requisitos  
- Conta no [Microsoft Azure](https://azure.microsoft.com/).  
- Ferramentas instaladas:  
    - [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)  
    - [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)  
    - Python 3.8+  
    - Bibliotecas necessárias (listadas em `requirements.txt`).  

## Configuração  
1. Clone o repositório:  
     ```bash  
     git clone <URL_DO_REPOSITORIO>  
     cd RagFinal  
     ```  
2. Instale as dependências:  
     ```bash  
     pip install -r requirements.txt  
     ```  
3. Configure os serviços do Azure seguindo as melhores práticas:  
     - Crie e configure um recurso do Azure Cognitive Search.  
     - Configure o Azure OpenAI para modelos generativos.  

## Uso  
1. Inicie a Function App localmente:  
     ```bash  
     func start  
     ```  
2. Personalize os parâmetros no arquivo de configuração para ajustar o comportamento do modelo.  
3. Faça chamadas para a API da Function App para testar as funcionalidades.

## Licença  
Este projeto está licenciado sob a [MIT License](LICENSE).  

## Contato  
Para dúvidas ou sugestões, entre em contato com o mantenedor do projeto.  
