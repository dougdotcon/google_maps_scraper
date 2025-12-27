# Google Maps Lead Scraper

Esta é uma ferramenta de automação robusta desenvolvida em Python para extrair leads de negócios do Google Maps. O projeto utiliza **Selenium** para navegação automatizada e **Tkinter** para oferecer uma interface gráfica intuitiva de configuração antes da execução.

## Funcionalidades

-   **Interface Gráfica (GUI)**: Configure os parâmetros de busca facilmente sem editar código.
-   **Busca por Múltiplos Termos**: Aceita várias palavras-chave (ex: "restaurantes, farmácias, advogados") e executa a busca sequencialmente.
-   **Localização Personalizável**: Define o ponto central da busca através de um endereço completo.
-   **Extração de Dados**: Coleta nome, endereço, telefone, website e link do Google Maps.
-   **Limitação de Resultados**: Configure o limite máximo de leads a serem buscados para cada termo.
-   **Exportação para Excel**: Salva os dados consolidados em um arquivo `.xlsx` com carimbo de data/hora para evitar sobrescrita.
-   **Modo Headless**: Opção para rodar o navegador em segundo plano (invisível).

## Pré-requisitos

Certifique-se de ter o **Python 3.8+** instalado em seu sistema.

### Instalação

1.  Clone este repositório ou baixe os arquivos.
2.  Instale as dependências necessárias executando:

bash
pip install -r requirements.txt


O arquivo `requirements.txt` inclui:
-   `selenium`
-   `webdriver-manager`
-   `pandas`
-   `openpyxl`

## Como Usar

1.  Execute o script principal:

bash
python scraper.py


2.  Uma janela de configuração abrirá com os seguintes campos:
    *   **Localização Alvo**: O endereço onde a busca será centrada.
    *   **Termos de Busca**: Digite os nichos ou palavras-chave separados por vírgula (ex: `marketing, consultoria, design`).
    *   **Máximo de Leads**: Quantidade de resultados a buscar *para cada termo*.
    *   **Modo Oculto**: Marque esta opção se não quiser ver o navegador abrindo.

3.  Clique em **"Iniciar Busca"**.

4.  O sistema irá:
    *   Abrir o Google Maps.
    *   Buscar o endereço alvo.
    *   Iterar sobre cada palavra-chave buscando empresas próximas.
    *   Extrair os dados disponíveis.
    *   Salvar tudo em um arquivo Excel (ex: `leads_marketing_167823.xlsx`) na pasta do projeto.

## Estrutura do Projeto

*   `scraper.py`: Script principal contendo a lógica de scraping e a interface Tkinter.
*   `browser.py`: Módulo auxiliar para gerenciamento do driver do Selenium e configurações do Chrome.
*   `requirements.txt`: Lista de bibliotecas Python necessárias.

## Notas

*   O script utiliza o Google Chrome. Certifique-se de ter o navegador instalado.
*   O tempo de execução depende da quantidade de termos e do limite de leads configurado.
*   O Google Maps pode apresentar variações no layout ou limitações de requisições excessivas (rate limiting). O script possui pausas (`sleep`) para tentar mitigar bloqueios, mas o uso excessivo deve ser evitado.