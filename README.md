# Sistema de Gerenciamento de Pedidos e Entregadores

## Requisitos Funcionais

### 1. Atribuir Pedido a Entregadores
- **Objetivo**: Atribuir um pedido a entregadores disponíveis dentro de um raio específico da localização.
- **Rota**: `POST /atribuir_pedido`
- **Entrada**:
  - `pedido_id`: Identificador único do pedido.
  - `latitude`: Latitude da localização do pedido.
  - `longitude`: Longitude da localização do pedido.
- **Processo**:
  1. O sistema verifica os entregadores disponíveis e próximos (dentro de um raio de 500 metros).
  2. Os entregadores são ordenados por saldo (quanto mais saldo, melhor).
  3. Se não encontrar entregadores dentro do raio, aumenta o raio em 500 metros e tenta novamente.
  4. O pedido é atribuído aos 3 entregadores mais próximos e com maior saldo.
- **Resposta**:
  - `{"message": "Pedido enviado aos entregadores", "candidatos": melhores_entregadores}`

### 2. Atualizar Localização do Entregador
- **Objetivo**: Permitir que o entregador atualize sua localização em tempo real.
- **Rota**: `POST /localizacao`
- **Entrada**:
  - `entregador_id`: Identificador único do entregador.
  - `latitude`: Latitude atual do entregador.
  - `longitude`: Longitude atual do entregador.
- **Processo**:
  1. O sistema recebe a nova localização do entregador e atualiza o banco de dados.
- **Resposta**:
  - `{"message": "Localização atualizada"}`

## Requisitos Não Funcionais

### 1. Desempenho
- **Objetivo**: Garantir que o sistema consiga encontrar um entregador disponível no máximo **em 3 minutos** de busca.
- **Descrição**:
  - O sistema deve ser capaz de buscar entregadores em tempo real e com o menor tempo de resposta possível. Caso a busca inicial (com raio de 500 metros) não encontre entregadores, o sistema irá aumentar progressivamente o raio de busca (em incrementos de 500 metros) até encontrar entregadores ou atingir o tempo limite de 3 minutos.
  - O tempo máximo para a busca de entregadores será de 3 minutos. Durante esse tempo, o sistema irá expandir a busca e processar até encontrar entregadores ou até que o tempo limite seja atingido.
  - **Critério de sucesso**: A busca por entregadores deverá ser completada dentro de 3 minutos ou o sistema deve retornar uma mensagem informando que não há entregadores disponíveis dentro do raio máximo especificado.



