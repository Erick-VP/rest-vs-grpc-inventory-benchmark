<!-- # DIRETRIZES ACADÊMICAS DO TCC

## Informações Básicas
* **Título:** Análise Comparativa de Desempenho na Agregação de Dados de Inventário: Uma Abordagem entre APIs REST (JSON) e gRPC (Protocol Buffers).
* **Curso:** Tecnologia em Sistemas de Computação (UESPI).
* **Formato Final:** Artigo Científico modelo SBC (mínimo 12 páginas).

## O Escopo
* **Problema:** O JSON causa gargalos pesados de CPU e rede ao trafegar lotes massivos de dados estruturados (como matrizes de inventário logístico local).
* **Objetivo Geral:** Medir e comparar latência, consumo de banda e throughput entre REST/JSON e gRPC na agregação de 1k, 50k e 100k itens de inventário.
* **A "Região Y" (Diferencial):** A literatura já compara gRPC vs JSON, mas geralmente focando em IoT ou telemetria. Este trabalho inova ao focar no estresse de payloads gigantes e altamente aninhados do setor logístico/comercial.

## Regras de Escrita (Prompting)
* Tom acadêmico, formal, coeso e direto.
* Proibido usar "encheção de linguiça". Focar em engenharia de software e análise de dados. -->

<!-- ## O Escopo e Diferencial
* **Problema:** O JSON causa gargalos de CPU e rede ao trafegar matrizes massivas de dados.
* **Diferencial Crítico:** Diferente de Tangudu (2026), que focou em **concorrência** (muitos usuários), este trabalho foca no **tamanho do payload** (volume de dados por requisição). Provamos o limite de ruptura da serialização textual vs. binária em inventários gigantes. -->



# DIRETRIZES ACADÊMICAS DO TCC (ATUALIZADO)

## Informações Básicas
* **Título:** Análise Comparativa de Desempenho na Agregação de Dados de Inventário: Uma Abordagem entre APIs REST (JSON) e gRPC (Protocol Buffers).
* **Curso:** Tecnologia em Sistemas de Computação (UESPI).
* **Formato Final:** Artigo Científico modelo SBC (mínimo 12 páginas).

## O Escopo e Diferencial
* **Problema:** O JSON causa gargalos de CPU e rede ao trafegar matrizes massivas de dados.
* **Diferencial Crítico:** Trabalhos seminais de 2026 (Tangudu) já consolidam o gRPC como padrão para microsserviços de alto desempenho em larga escala. Este TCC estende essa fronteira ao testar a eficiência da serialização binária contra o JSON em payloads de inventário que variam de 1k a 100k registros, focando no limite de ruptura do processamento de texto plano


## Regras de Escrita (Diretrizes do Professor)
* **Densidade de Citações:** Quase toda oração que contenha afirmação técnica deve ter repertório/citação. Intercalar apenas quando for análise direta dos meus resultados.
* **Tom:** Acadêmico, formal e baseado em evidências empíricas.