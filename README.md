# Implementação Blockchain

Professor: [Danilo Curvelo](https://github.com/danilocurvelo)

Aluno: [Daniel Luan Lourenço de Lima](https://github.com/danieluan)

Ao longo da primeira unidade da disciplina IMD0913 - Blockchain e Aplicações Descentralizadas foi implementado uma estrutura de dado semelhante ao Blokchain do Bitcoin, usando validações de PoW (Proof Of Work), Assinaturas digitais e, por fim, uma API para realizar o consenso dos nós cadastrados na rede.

# Blockchain

## Endpoints

### Endpoint: /transactions/create [POST]
- **Descrição**: Cria uma nova transação e a adiciona à mempool (lista de transações).
- **Parâmetros**:
    - sender: Endereço do remetente da transação.
    - recipient: Endereço do destinatário da transação.
    - amount: Valor da transação.
    - privWifKey: Chave privada para assinar a transação.
- **Respostas**:
    - 200: Transação em processamento.
    - 406: Falha ao processar devido a dados ausentes ou inválidos.

### Endpoint: /chain [GET]
- **Descrição**: Retorna todos os blocos presentes na cadeia no momento.
- **Respostas**:
    - 200: Retorna a cadeia de blocos no formato JSON.

### Endpoint: /transactions/mempool [GET]
- **Descrição**: Retorna todas as transações presentes na mempool no momento.
- **Respostas**:
    - 200: Retorna a mempool no formato JSON.

### Endpoint: /mine [GET]
- **Descrição**: Realiza a mineração de um novo bloco e o adiciona à cadeia.
- **Respostas**:
    - Retorna os detalhes do bloco recém-minerado no formato JSON.

### Endpoint: /nodes/register [POST]
- **Descrição**: Registra nós adicionais na rede.
- **Parâmetros**:
    - nodes: Lista de URLs dos nós a serem registrados.
- **Respostas**:
    - 200: Nós registrados com sucesso.
    - 400: Erro se a lista de nós estiver vazia.

### Endpoint: /nodes/resolve [GET]
- **Descrição**: Executa a resolução de conflitos entre os blocos da cadeia na rede.
- **Respostas**:
    - 200: Se a cadeia foi atualizada com sucesso.
    - Se nenhuma cadeia maior e válida for encontrada: Retorna mensagem indicando a ausência de cadeias maiores e válidas.


# Como executar

## Configuração 

O blockchain foi inteiramente implementado usando `Python`, por tanto é necessário ter Python3+ e pip instalado. Sendo assim é recomendado utilizar um ambiente isolado para executar o programa.

Rode os comandos para baixar o repositório localmente e acessá-lo no terminal.

```bash
git clone https://github.com/DanieLuan/blockchain-implementation.git
```
```bash
cd blockchain-implementation
```

Após isso, certifique-se de baixar o virtualenv.

```bash
pip install virtualenv
```

Agora crie o ambiente na pasta local usando o nome de sua preferência. Nesse caso estamos usando `venv`.

```bash
virtualenv venv
```

Use o comando abaixo para entrar no ambiente virtual criado.

```bash
source venv/bin/activate
```

Por fim, instale as dependências necessárias.

```bash
pip install -r requirements.txt
```

## Execução

Para rodar um nó, basta rodar o programa usando.

```bash
blockchain-api/bin/python api.py --port <port_number>
```

A flag `--port` foi utilizada para facilitar a implementação de múltiplas instâncias do mesmo programa em portas diferentes do mesmo computador. As portas usadas para os testes foram as `5000` e `5001`, qualquer outra porta deverá ser cadastrada usando o devido endpoint.

