import requests


## TESTE COMMIT

TOKEN = "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"

headers = {
    'Authorization': f'token {TOKEN}'  # Autenticação com token
}

# Substitua pelos dados do seu repositório
owner = "gabrielmchlmnn"
repo = "codeSmellsFinder"

url = f"https://api.github.com/repos/{owner}/{repo}/commits"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())
    commit_data = response.json()[0]
    commit_sha = commit_data["sha"]

    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        commit_data = response.json()
        files = commit_data.get('files', [])
        codigo = ""
        for file in files:

            print("\n \n \n ==================================================== \n \n \n")
            print(file)
            print(file.get('filename')+" < - Arquivo:")
            print(file.get('patch', '') ) # Adicionando o "diff" do código alterado

        print(codigo)

    print(f"O código do último commit para o arquivo é: {commit_sha}")
else:
    print(response.reason)
    print("Erro ao buscar o commit:", response.status_code)
