# ESTADO DA ARTE E FICHAMENTO

## Matriz de Artigos Lidos

### Artigo 1 (O mais próximo do tema)
* **Título:** Comparative study of REST and gRPC for microservices in established software architectures.
* **Autores/Ano:** M Johansson, O Isabella (2023).
* **O que testaram:** Avaliaram a diferença de performance entre REST e gRPC em um sistema real de microsserviços voltado para o planejamento de Cadeia de Suprimentos (Supply Chain).
* **A Lacuna (brecha):** O estudo focou em requisições de planejamento e tráfego geral. Eles não isolaram e não estressaram o limite de transferência de payloads massivos (matrizes gigantes de agregação de estoque). O meu TCC preenche essa lacuna ao focar no volume e peso do dado, e não apenas na arquitetura geral.

### Artigo 2 (O foco em IoT)
* **Título:** Investigating Efficient Binary Serialization Protocols for Hybrid TN/NT Networks for Massive IoT Devices and M2M Systems.
* **Autores/Ano:** N Kumar, P Pagano (2025).
* **O que testaram:** Provaram que o Protocol Buffers é muito superior ao JSON no domínio de logística global.
* **A Lacuna (brecha):** A aplicação deles é 100% focada em dispositivos IoT (Internet das Coisas) e telemetria de sensores, que trafegam dados minúsculos (alguns bytes por vez). O meu TCC testa o extremo oposto: servidores trafegando blocos massivos e aninhados de megabytes de inventário de uma só vez.

### Artigo 3 (O foco Científico)
* **Título:** Improving throughput of CERN's multi-language distributed online data processing platform.
* **Autores/Ano:** F Andreuzzi (2021).
* **O que testaram:** Avaliaram a agregação de dados em larga escala usando gRPC e HTTP/2.
* **A Lacuna (A sua brecha):** O cenário é altamente focado em física de partículas (CERN) e processamento científico. Falta na literatura trazer essa mesma lógica de otimização de agregação de dados para o cenário comercial/logístico do dia a dia, que é o que o meu TCC propõe.

### Artigo 4 (A Base de Performance em Larga Escala)
* **Título:** A Comparative Design Study of REST, GraphQL and gRPC APIs for Large-Scale Applications.
* **Autor/Ano:** Ramesh Tangudu (2026).
* **O que testou:** Realizou uma análise comparativa de design entre REST, GraphQL e gRPC, focando em escalabilidade e performance para sistemas corporativos e cloud-native.
* **Resultados Chave:** Confirmou que o gRPC atinge performance superior através de serialização binária e uso de HTTP/2, sendo a escolha ideal para comunicação interna entre microsserviços.
* **A Lacuna (brecha):** Embora o estudo de Tangudu (2026) forneça métricas de latência e throughput sob carga de requisições concorrentes, ele mantém a análise no nível de design arquitetural e padrões de carga genéricos. Ele não explora especificamente o comportamento dos protocolos diante de matrizes massivas de dados de inventário (o seu cenário logístico), onde o peso do payload em si é o principal vilão.

### Ainda a ser atualizado
### Artigo 5 (Viabilidade)
* **Título:** Uma Análise Comparativa dos Protocolos REST e gRPC na Manutenção e Evolução de Microsserviços
* **Autor/Ano:** Lucas A. F. Pereira.
* **O que testou:** Realizou uma análise comparativa de design entre REST, GraphQL e gRPC, focando em escalabilidade e performance para sistemas corporativos e cloud-native.
* **Resultados Chave:** Confirmou que o gRPC atinge performance superior através de serialização binária e uso de HTTP/2, sendo a escolha ideal para comunicação interna entre microsserviços.
* **A Lacuna (brecha):** Embora o estudo de Tangudu (2026) forneça métricas de latência e throughput sob carga de requisições concorrentes, ele mantém a análise no nível de design arquitetural e padrões de carga genéricos. Ele não explora especificamente o comportamento dos protocolos diante de matrizes massivas de dados de inventário (o seu cenário logístico), onde o peso do payload em si é o principal vilão.
