# ESPECIFICAÇÃO DE ARQUITETURA E CÓDIGO

## Stack Tecnológica
* **Linguagem/Framework:** Java 17+ com Spring Boot. (a ser pensado ainda)
* **Arquiteturas Alvo:** REST (com JSON) e gRPC (usando dependência grpc-spring-boot-starter).
* **Gerador de Dados (Mock):** Biblioteca Datafaker.
* **Teste de Carga:** K6 (Grafana) ou JMeter.

## Modelagem de Dados (O Payload)
* O objeto base será `ItemInventario`.
* Propriedades obrigatórias:
  * `id` (UUID ou String)
  * `nomeProduto` (String)
  * `categoria` (String)
  * `quantidade` (Integer)
  * `precoUnitario` (Double ou BigDecimal)
  * `galpaoOrigem` (String)

## Regras de Desenvolvimento (Prompting para Código)
* O código deve ser simples e focado APENAS em responder a requisição o mais rápido possível.
* Não criar conexões reais com banco de dados (o gargalo a ser medido é o da rede e da serialização, não do banco). O Datafaker deve gerar as listas diretamente na memória RAM da aplicação.