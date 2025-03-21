import requests
import json
from radon.complexity import cc_visit
import jedi
import difflib
import re


TOKEN = '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'


def remover_diff(codigo):
    """
    Remove marcas de diff (ex: @@ -0,0 +1,26 @@) do código.
    """
    # Remover linhas de diff (como @@ -0,0 +1,26 @@)
    codigo_limpo = re.sub(r'^\+\+.*\n|^\-\-.*\n|^@@.*\n', '', codigo)

    # Limpar qualquer outro caractere indesejado, como sinais de adição (+) ou remoção (-)
    codigo_limpo = re.sub(r'^\+|^\-', '', codigo_limpo, flags=re.MULTILINE)

    return codigo_limpo

# Função para buscar repositórios no GitHub com "code smells" no nome ou descrição, paginando até 50 páginas
def buscar_datasets_code_smells():
    url = "https://api.github.com/search/repositories"
    params = {
        'q': 'code smells',  # Pesquisa por repositórios relacionados a "code smells"
        'sort': 'stars',  # Ordenar por popularidade (número de estrelas)
        'order': 'desc',
        'per_page': 30  # Definindo o máximo de itens por página
    }
    headers = {
        'Authorization': f'token {TOKEN}'  # Autenticação com token
    }

    all_repositories = []

    # Vamos fazer um loop pelas páginas até 50
    for page in range(1, 2):
        params['page'] = page  # Adiciona o número da página à requisição
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Se a página vier vazia (não há mais resultados), podemos parar
            if len(data['items']) == 0:
                break

            all_repositories.extend(data['items'])  # Adiciona os repositórios encontrados nesta página à lista
            print(f"Página {page} processada. {len(data['items'])} repositórios encontrados.")

        else:
            print(f"Erro ao buscar dados na página {page}: {response.status_code}")
            break

    return all_repositories


# Função para buscar commits de um repositório específico
def buscar_commits_repositorio(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    headers = {
        'Authorization': f'token {TOKEN}'  # Autenticação com token
    }

    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar commits: {response.status_code}")
        return []


# Função para buscar o código de um commit específico
def buscar_codigo_commit(owner, repo, sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"

    headers = {
        'Authorization': f'token {TOKEN}'  # Autenticação com token
    }

    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        commit_data = response.json()
        # Extraindo o código do arquivo alterado do commit
        files = commit_data.get('files', [])
        codigo = ""
        for file in files:
            if file.get('filename').endswith('.py'):  # Supondo que estamos trabalhando com Python
                codigo += file.get('patch', '')  # Adicionando o "diff" do código alterado
        return codigo
    else:
        print(f"Erro ao buscar código do commit: {response.status_code}")
        return ""


def identificar_tipo_bad_smell(codigo):
    tipo_detectado = []

    try:
        tipos = {
            'duplicacao': detectar_duplicacao(codigo),
            'longa_funcao': detectar_funcoes_largas(codigo),
            'nome_inadequado': detectar_nomes_inadequados(codigo),
            'complexidade': analisar_complexidade(codigo),
            'baixo_coesao': analisar_coesao(codigo),
            'alto_acoplamento': analisar_acoplamento(codigo)
        }


        for tipo, problema in tipos.items():
            if problema:
                tipo_detectado.append(tipo)
    except Exception as e:
        print("erro ao analisar repositorio")

    return tipo_detectado if tipo_detectado else ['Não identificado']

# Funções de detecção mais específicas

def detectar_duplicacao(codigo):
    # Vamos dividir o código em linhas e comparar se algum bloco se repete
    linhas = codigo.split('\n')
    duplicados = []

    # Comparar cada linha com as outras
    for i in range(len(linhas)):
        for j in range(i + 1, len(linhas)):
            # Verificar a similaridade entre duas linhas
            if difflib.SequenceMatcher(None, linhas[i], linhas[j]).ratio() > 0.8:  # Limite de 80% de similaridade
                duplicados.append((linhas[i], linhas[j]))

    # Se existirem duplicações, retorna a lista
    if duplicados:
        return ['duplicação de código']
    return []

def detectar_funcoes_largas(codigo):
    # Aqui você pode procurar por funções muito grandes ou longas
    if len(codigo.split('\n')) > 50:  # Exemplo: função com mais de 50 linhas
        return ['função longa']
    return []

def detectar_nomes_inadequados(codigo):
    # Detecta padrões de nomes ruins (exemplo simples de encontrar nomes curtos ou não descritivos)
    palavras_ruins = ['tmp', 'var', 'foo', 'bar']
    for palavra in palavras_ruins:
        if palavra in codigo:
            return ['nomes inadequados']
    return []

def analisar_complexidade(codigo):

    codigo_limpo = remover_diff(codigo)
    resultado = cc_visit(codigo_limpo)
    problemas = []

    for funcao in resultado:
        if funcao.complexity > 10:  # Um limite arbitrário para complexidade alta
            problemas.append({
                'nome': funcao.name,
                'complexidade': funcao.complexity
            })

    return problemas

# Função para detectar complexidade alta
def identificar_complexidade(codigo):
    problemas = analisar_complexidade(codigo)
    if problemas:
        return ['complexidade alta']
    return []


def analisar_coesao(codigo):
    # Verificação de coesão de uma classe, ou seja, se o código está organizado e cada parte tem uma função clara
    return []  # Implementar a análise de coesão aqui

def analisar_acoplamento(codigo):
    # Verificação do acoplamento entre classes, funções e módulos
    return []  # Implementar a análise de acoplamento aqui


# Função para salvar dados em um arquivo JSON
def salvar_dados_em_json(dados, nome_arquivo='datasets_code_smells.json'):
    with open(nome_arquivo, 'w') as f:
        json.dump(dados, f, indent=4)
    print(f"Dados salvos em {nome_arquivo}")


# Função principal
def main():
    # Buscar datasets sobre code smells
    datasets = buscar_datasets_code_smells()

    # Processar e armazenar os dados
    if datasets:
        dados_formatados = []
        for repo in datasets:
            print(f'Processando repositório: {repo["name"]}')
            # Buscar commits do repositório
            owner = repo['owner']['login']
            repo_name = repo['name']
            commits = buscar_commits_repositorio(owner, repo_name)

            codigo_repositorio = ""
            # Se houver commits, buscamos o código de um commit recente
            if commits:
                sha_ultimo_commit = commits[0]['sha']
                codigo_repositorio = buscar_codigo_commit(owner, repo_name, sha_ultimo_commit)

            # Identificar o tipo de "bad smell" no código
            tipo_bad_smell = identificar_tipo_bad_smell(codigo_repositorio)

            # Adicionar informações do repositório, código e tipo de bad smell
            dados_formatados.append({
                'nome': repo['name'],
                'descricao': repo['description'],
                'url': repo['html_url'],
                'estrelas': repo['stargazers_count'],
                'linguagem': repo['language'],
                'data_criacao': repo['created_at'],
                'data_atualizacao': repo['updated_at'],
                'codigo': codigo_repositorio,  # Armazenando o código alterado
                'tipo_bad_smell': tipo_bad_smell  # Armazenando o tipo de "bad smell"
            })

        # Salvar em arquivo JSON
        salvar_dados_em_json(dados_formatados)
    else:
        print("Nenhum dataset encontrado.")


if __name__ == "__main__":
    main()
