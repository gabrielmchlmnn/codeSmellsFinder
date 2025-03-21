import json


# Função para carregar e percorrer o arquivo JSON
def percorrer_json(caminho_arquivo, chaves_desejadas):
    with open(caminho_arquivo, 'r') as f:
        # Carregar o conteúdo do arquivo JSON
        dados = json.load(f)

        # Função recursiva para percorrer e imprimir as chaves desejadas
        def imprimir_chaves(dados):
            if isinstance(dados, dict):  # Se for um dicionário
                for chave, valor in dados.items():
                    if chave in chaves_desejadas and valor != '':
                        if chave == 'linguagem':
                            linguagem = valor
                        valor_limitado = valor[:50] if isinstance(valor, str) else valor

                        if chave == 'codigo':
                            print(f"Linguagem: {linguagem}")

                            print(f"{chave}: {valor_limitado} ...")
                    if isinstance(valor, (dict, list)):  # Se o valor for um dicionário ou lista, percorra
                        imprimir_chaves(valor)
            elif isinstance(dados, list):  # Se for uma lista, percorra cada item
                for item in dados:
                    imprimir_chaves(item)

        # Chamar a função para imprimir as chaves desejadas
        imprimir_chaves(dados)


# Caminho do arquivo JSON
caminho_arquivo = 'datasets_code_smells.json'

# Defina as chaves que você deseja imprimir
chaves_desejadas = ['linguagem', 'codigo']

# Chamar a função
percorrer_json(caminho_arquivo, chaves_desejadas)
