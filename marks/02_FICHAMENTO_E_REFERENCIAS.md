<!-- ### Artigo X
* **Título:**
* **Autor/Ano:**
* **O que fez:** -->
# ESTADO DA ARTE E FICHAMENTO

## Matriz de Artigos Lidos

### Artigo 1 (O mais próximo do tema)
* **Título:** Comparative study of REST and gRPC for microservices in established software architectures.
* **Autores/Ano:** M Johansson, O Isabella (2023).
* **O que testaram:** Avaliaram a diferença de performance entre REST e gRPC em um sistema real de microsserviços voltado para o planejamento de Cadeia de Suprimentos (Supply Chain).
* **A Lacuna (brecha):** O estudo focou em requisições de planejamento e tráfego geral. Eles não isolaram e não estressaram o limite de transferência de payloads massivos (matrizes gigantes de agregação de estoque). O meu TCC preenche essa lacuna ao focar no volume e peso do dado, e não apenas na arquitetura geral.

### Artigo 2 (O foco em IoT)
* **Título:** Investigating Efficient Binary Serialization Protocols for Hybrid TN/NT Networks for Massive IoT Devices and M2M Systems. (https://jlab-ports.cnit.it/wp-content/uploads/2025/12/Kumar_Natesh_Thesis_2025.pdf)
* **Autores/Ano:** N Kumar, P Pagano (2025).
* **O que testaram:** Provaram que o Protocol Buffers é muito superior ao JSON no domínio de logística global.
* **A Lacuna (brecha):** A aplicação deles é 100% focada em dispositivos IoT (Internet das Coisas) e telemetria de sensores, que trafegam dados minúsculos (alguns bytes por vez). O meu TCC testa o extremo oposto: servidores trafegando blocos massivos e aninhados de megabytes de inventário de uma só vez. ( o dele é só largura de banda, então não envia dados massivos)

### Artigo 3 (O foco Científico)
* **Título:** Improving throughput of CERN's multi-language distributed online data processing platform.
* **Autores/Ano:** F Andreuzzi (2021).
* **O que testaram:** Avaliaram a agregação de dados em larga escala usando gRPC e HTTP/2.
* **A Lacuna (A sua brecha):** O cenário é altamente focado em física de partículas (CERN) e processamento científico. Falta na literatura trazer essa mesma lógica de otimização de agregação de dados para o cenário comercial/logístico do dia a dia, que é o que o meu TCC propõe.

### Artigo 4 (A Base de Performance em Larga Escala)
* **Título:** A Comparative Design Study of REST, GraphQL and gRPC APIs for Large-Scale Applications. (https://www.theseus.fi/bitstream/handle/10024/904498/Reichersd%c3%b6rfer_Sven.pdf?sequence=2&isAllowed=y)
* **Autor/Ano:** Ramesh Tangudu (2026).
* **O que testou:** Realizou uma análise comparativa de design entre REST, GraphQL e gRPC, focando em escalabilidade e performance para sistemas corporativos e cloud-native.
* **Resultados Chave:** Confirmou que o gRPC atinge performance superior através de serialização binária e uso de HTTP/2, sendo a escolha ideal para comunicação interna entre microsserviços.
* **A Lacuna (brecha):** Embora o estudo de Tangudu (2026) forneça métricas de latência e throughput sob carga de requisições concorrentes, ele mantém a análise no nível de design arquitetural e padrões de carga genéricos. Ele não explora especificamente o comportamento dos protocolos diante de matrizes massivas de dados de inventário (o seu cenário logístico), onde o peso do payload em si é o principal vilão.

### Ainda a ser atualizado
### Artigo 5 (Viabilidade)
* **Título:** Uma Análise Comparativa dos Protocolos REST e gRPC na Manutenção e Evolução de Microsserviços
* **Autor/Ano:** Lucas A. F. Pereira. (2024)
* **O que testou:** Fez uma mineração de repositórios do GitHub que usam REST e gRPC com base nas estrelas, forks, etc.
* **Resultados Chave:** Confirmou que tanto REST e gRPC são totalmente viáveis em projetos, cada um tem sua vantagem.
* **A Lacuna (brecha):** Ele só fala de viabilidade, não fala nada sobre testes ou do cenários de grandes payloads.

### Artigo 6 (Embasamento/contextualização)
* **Título:** Analysis of Microservice Evolution using Cohesion Metrics (https://dl.acm.org/doi/epdf/10.1145/3559712.3559716)
* **Autor/Ano:**: Mateus Gabi Moreira and Breno Bernard Nicolau De França (2022)

### Artigo 7
* **Título:** Building microservices: designing fine-grained systems (https://books.google.com.br/books?hl=pt-BR&lr=&id=ZvM5EAAAQBAJ&oi=fnd&pg=PT16&dq=Newman,+S.+(2021).+Building+Microservices&ots=uibl9v5HXn&sig=FC3cQk6_wUItqx_9Lq6F9czy5fI#v=onepage&q=Newman%2C%20S.%20(2021).%20Building%20Microservices&f=false) (https://cdn.studio.f5.com/files/k6fem79d/production/127ba8fd31c38d7e575ed000a58872a6c87be19a.pdf)
* **Autor/Ano:** S Newman - 2021 
* **O que fez:** Fer um livro explicando a construção sobre microserviços e seu fluxo.

### Artigo 8
* **Título:** API Management Patterns for Public, Partner, and Group Web API Initiatives with a Focus on Collaboration (https://dl.acm.org/doi/epdf/10.1145/3489449.3490012)
* **Autor/Ano:** Gloria Bondel, Andre Landgraf, Florian Matthes (2022)
* **O que fez:** Explica como é a conexão da API com os protocolos (essencial para entender microserviços)

### Artigo 9
* **Título:** Architectural Styles and the Design of Network-based Software Architectures (https://roy.gbiv.com/pubs/dissertation/fielding_dissertation.pdf)
* **Autor/Ano:** Roy Thomas Fielding (2000)
* **O que fez:** Fez um artigo famoso sobre a arquitetura REST na época. 

### Artigo 10 (Referencial téorico, metodologia e justificativa)
* **Título:** Performance Characterization of Communication
Protocols in Microservice Applications (https://scispace.com/pdf/performance-characterization-of-communication-protocols-in-44382a5nrh.pdf)
* **Autor/Ano:** Prajwal Kiran Kumar, Radhika Agarwal, Rahul Shivaprasad (2021)
* **O que fez:** Viu as perfomances dos protocolos existentes e testou usando arquivos leves (100kb-10000kb) para teste matemáticos e fins comparativos
* **Brecha:** O que vou fazer é usar arquivos brutos para testar gargalos e mostrar a importancia para o setor comercial (logística)