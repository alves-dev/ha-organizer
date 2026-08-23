# HA Organizer — Especificação do beta

## 1. Contexto

Instalações do Home Assistant crescem continuamente e podem acumular inconsistências em categorias, áreas, zonas, nomes de entidades e aliases. O Home Assistant oferece interfaces para editar esses elementos, mas não apresenta uma visão única para auditar a organização da instalação nem acompanhar uma revisão que pode levar várias sessões.

O **HA Organizer** será uma custom integration que adiciona um painel próprio ao Home Assistant. Na primeira versão, a integração será exclusivamente de leitura sobre os recursos do Home Assistant: ela deve inventariar, comparar, validar e acompanhar revisões, mas nunca alterar entidades, categorias, áreas, zonas, aliases ou configurações nativas.

O nome é provisório e não deve bloquear a implementação.

## 2. Objetivo do beta

Entregar uma central visual que permita ao administrador:

- escolher quais aspectos da instalação deseja revisar;
- visualizar inconsistências e itens que exigem atenção;
- organizar o trabalho em instalações pequenas ou grandes;
- marcar itens como revisados ou ignorados;
- continuar a revisão em outra sessão;
- detectar quando algo previamente revisado mudou;
- abrir ou localizar o recurso correspondente no Home Assistant para corrigi-lo manualmente.

## 3. Princípios

1. **Read-only sobre o Home Assistant:** o beta não renomeia, cria, remove ou atualiza recursos nativos.
2. **Persistência apenas do próprio Organizer:** preferências, regras, progresso, justificativas e fingerprints podem ser armazenados pela integração.
3. **Determinístico:** não haverá IA no beta.
4. **Opt-in por módulo:** o usuário escolhe quais revisões deseja ativar.
5. **Progresso confiável:** uma revisão deve ficar desatualizada se os dados que a originaram mudarem.
6. **Explicável:** toda issue deve informar o que foi encontrado, por que importa e quais recursos estão envolvidos.
7. **Escalável:** tabelas devem suportar busca, filtros, ordenação e paginação ou virtualização.

## 4. Escopo funcional

O beta terá os módulos:

1. Overview
2. Categories
3. Areas
4. Zones
5. Entity IDs
6. Exposed Entities & Aliases

## 5. Modelo de status

Não usar um único status para representar simultaneamente a análise técnica e o andamento do usuário. Cada item possui dois eixos independentes.

### 5.1 Resultado calculado (`compliance_status`)

Definido automaticamente a cada análise:

| Valor | Significado |
| --- | --- |
| `compliant` | O item atende às regras habilitadas. |
| `non_compliant` | Existe uma divergência objetiva. |
| `attention` | A integração encontrou uma condição que exige decisão humana. |
| `not_applicable` | Nenhuma regra habilitada se aplica ao item. |

### 5.2 Andamento do usuário (`review_status`)

| Valor | Significado |
| --- | --- |
| `pending` | Ainda não revisado. Valor inicial. |
| `reviewed` | O usuário conferiu o item no estado atual. |
| `ignored` | A condição foi aceita intencionalmente. Deve permitir justificativa opcional. |
| `stale` | O item era `reviewed` ou `ignored`, mas os dados relevantes mudaram. |

### 5.3 Regras de transição

- Marcar um item não altera seu `compliance_status`.
- `reviewed` e `ignored` devem armazenar um fingerprint dos dados analisados.
- Se o fingerprint atual for diferente do armazenado, o status passa a `stale`.
- Se uma divergência desaparecer, `compliance_status` passa automaticamente para `compliant`.
- Um item `compliant` pode continuar `pending`: conformidade e revisão são conceitos distintos.
- O usuário pode revisar novamente um item `stale`, gerando um novo fingerprint.
- Se o recurso não existir mais, remover o item ativo do inventário. O histórico não é obrigatório no beta.

### 5.4 Fingerprint

Gerar um hash estável a partir de uma representação canônica contendo somente os campos relevantes ao módulo e à regra. Não incluir campos voláteis, como estado atual de sensores, timestamps de atualização ou ordem não semântica de listas.

Exemplo conceitual:

```text
sha256(module + item_id + enabled_rule_versions + canonical_relevant_data)
```

O fingerprint deve mudar quando a revisão humana precisar ser refeita, e não a cada atualização normal do Home Assistant.

## 6. Onboarding e configuração

Na primeira abertura, mostrar os módulos disponíveis com uma explicação curta e um toggle para ativação. Todos podem ser habilitados depois.

Configuração mínima:

- módulos habilitados;
- regras habilitadas em cada módulo;
- configuração do padrão de `entity_id`;
- preferências de normalização;
- severidade configurável apenas se isso não aumentar muito o escopo.

Preferências de normalização sugeridas:

- comparação case-insensitive;
- ignorar acentos;
- normalizar espaços, hífens e underscores;
- comparar singular/plural fica fora do beta;
- similaridade semântica fica fora do beta.

## 7. Overview

Página inicial com visão consolidada.

### 7.1 Conteúdo

- módulos habilitados;
- progresso geral e por módulo;
- quantidade por `compliance_status`;
- quantidade por `review_status`;
- itens `stale` em destaque;
- data/hora da última análise;
- botão para atualizar a análise;
- atalhos para os módulos com pendências.

### 7.2 Métricas

- `review_progress = reviewed_or_ignored_current / total_reviewable_items`;
- conformidade deve ser exibida separadamente do progresso;
- não misturar “80% revisado” com “80% conforme”.

## 8. Categories

### 8.1 Ativação

O usuário habilita a revisão de categorias e escolhe os escopos a comparar. No beta:

- automations;
- scripts.

O design deve permitir novos escopos no futuro.

### 8.2 Categoria canônica

Para fins de comparação, normalizar o nome da categoria e criar uma linha lógica. O Organizer não cria uma nova categoria no HA.

Exemplo:

| Categoria detectada | Automations | Scripts | Resultado |
| --- | --- | --- | --- |
| Security | Sim | Sim | Conforme |
| Presence | Sim | Não | Divergente |
| Notification / Notifications | Sim | Sim | Atenção: nomes diferentes |

### 8.3 Verificações

- categoria existente em todos os escopos selecionados;
- categorias com nomes iguais após normalização, mas grafias diferentes;
- categorias sem nenhum item associado, quando essa informação estiver disponível de forma estável;
- quantidade de automações e scripts associados;
- categoria nova ainda não revisada;
- categoria previamente revisada cujo nome, presença nos escopos ou associações relevantes mudou.

### 8.4 Interação

- busca e filtro por resultado e andamento;
- expansão da categoria para listar recursos associados;
- marcar como revisada;
- ignorar com justificativa opcional;
- link para as páginas nativas relevantes quando tecnicamente possível;
- nenhuma ação de criação, renomeação ou associação.

## 9. Areas

### 9.1 Objetivo

Permitir a revisão progressiva da estrutura física/lógica da instalação e dos recursos associados a cada área.

### 9.2 Visão da lista

- nome da área;
- andar, quando houver;
- quantidade de dispositivos;
- quantidade de entidades diretamente associadas;
- quantidade de entidades efetivamente relacionadas por dispositivo;
- issues encontradas;
- resultado calculado;
- andamento da revisão.

### 9.3 Verificações

- áreas com nomes duplicados após normalização;
- áreas sem dispositivos e sem entidades;
- dispositivos sem área;
- entidades gerenciáveis sem área e sem dispositivo associado;
- divergência entre a área da entidade e a área do dispositivo, quando aplicável;
- nomes fora das regras simples configuradas;
- mudança no conjunto relevante de dispositivos ou entidades após a revisão.

Ausência de área não deve ser automaticamente tratada como erro para todo tipo de entidade. Casos sem regra objetiva devem usar `attention`.

### 9.4 Detalhe da área

- dados da área;
- dispositivos relacionados;
- entidades relacionadas;
- issues agrupadas;
- filtros por domínio e integração;
- ação de marcar a área como revisada no Organizer.

## 10. Zones

### 10.1 Objetivo

Inventariar e revisar as zonas geográficas configuradas, sem editar sua geometria ou propriedades.

### 10.2 Visão da lista

- nome;
- identificador;
- ícone, quando definido;
- raio;
- estado passivo/ativo, quando disponível;
- coordenadas apresentadas de forma reduzida;
- resultado calculado;
- andamento da revisão.

Evitar exibir coordenadas com destaque desnecessário. Elas são dados potencialmente sensíveis da residência.

### 10.3 Verificações determinísticas

- nomes duplicados após normalização;
- nomes genéricos ou vazios, se a API permitir tal condição;
- zonas com mesmo centro e raio, ou configuração praticamente idêntica;
- sobreposição relevante entre zonas como `attention`, nunca como erro automático;
- raio muito pequeno ou muito grande somente se o usuário habilitar limites explícitos;
- zona nova ou alterada depois de revisada;
- listagem de entidades `person` ou `device_tracker` relacionadas não é necessária no beta, mas a arquitetura não deve impedir essa evolução.

### 10.4 Observações

- A zona `home` pode exigir tratamento especial e não deve ser considerada uma duplicidade comum sem análise específica.
- Zonas sobrepostas podem ser intencionais; portanto, devem poder ser revisadas ou ignoradas.
- O beta não precisa analisar automações que usam cada zona.

## 11. Entity IDs

### 11.1 Objetivo

Encontrar entidades cujo `entity_id` não segue a convenção escolhida pelo usuário. O Home Assistant permite que o usuário escolha como ordenar e renomear seus IDs; o Organizer audita a aplicação consistente dessa escolha.

Referência: <https://www.home-assistant.io/blog/2026/08/05/release-20268/#your-entity-ids-your-choice>

### 11.2 Configuração do padrão

Oferecer dois modos:

1. **Construtor visual**, combinando tokens como área, dispositivo, entidade e texto fixo.
2. **Regex avançada**, opcional.

Exemplos conceituais:

```text
<domain>.<area>_<device>_<entity>
<domain>.<device>_<entity>
```

Permitir configurar exceções por domínio, pois nem todas as entidades possuem área ou dispositivo.

### 11.3 Verificações

- formato inválido segundo o padrão;
- ausência de token obrigatório;
- domínio excluído da política;
- colisão do nome normalizado;
- IDs gerados automaticamente com sufixos suspeitos, como `_2`, apenas como `attention`;
- entidades sem dados suficientes para avaliar o padrão como `not_applicable` ou `attention`, conforme a regra.

### 11.4 Tabela

- `entity_id` atual;
- nome exibido;
- área;
- dispositivo;
- domínio;
- integração/plataforma;
- padrão esperado ou motivo pelo qual não foi possível calculá-lo;
- resultado e andamento.

O padrão esperado é uma sugestão visual, não uma ação de rename.

## 12. Exposed Entities & Aliases

Este módulo faz parte obrigatória do beta, mas continua sem análise por IA.

### 12.1 Objetivo

Dar visibilidade centralizada às entidades expostas a assistentes, seus nomes efetivos e aliases, facilitando a identificação determinística de ambiguidades.

### 12.2 Dados exibidos

- `entity_id`;
- nome da entidade;
- nome efetivo/friendly name, quando aplicável;
- dispositivo;
- área;
- domínio;
- aliases;
- assistentes para os quais está exposta;
- status disabled/hidden/unavailable quando relevante;
- resultado calculado;
- andamento da revisão.

O backend atual do Home Assistant possui API WebSocket para listar entidades expostas. Usar APIs públicas/estáveis disponíveis na versão mínima suportada e encapsular diferenças de versão.

Referência: <https://github.com/home-assistant/core/blob/dev/homeassistant/components/homeassistant/exposed_entities.py>

### 12.3 Verificações determinísticas

- duas entidades expostas com o mesmo nome normalizado;
- aliases idênticos entre entidades diferentes;
- alias de uma entidade igual ao nome de outra entidade;
- aliases duplicados dentro da mesma entidade;
- diferenças apenas de caixa, acentos, espaços, hífens ou underscores;
- nome ou alias excessivamente genérico a partir de uma pequena lista configurável, como `luz`, `sensor` ou `temperatura`;
- entidades homônimas sem área, ou na mesma área, com maior severidade;
- entidade exposta que está desabilitada, indisponível ou não existe mais, quando detectável;
- entidade exposta sem alias não é, por padrão, um problema;
- aliases semanticamente semelhantes ficam fora do beta.

### 12.4 Agrupamento de ambiguidades

Uma colisão deve ser representada como um finding que referencia todas as entidades envolvidas, e não como várias issues independentes sem relação.

Exemplo:

```text
Chave normalizada: "luz escritorio"

- light.desk: alias "Luz do escritório"
- light.ceiling: nome "Luz do escritório"
```

### 12.5 Filtros

- assistente;
- área;
- domínio;
- com/sem aliases;
- com/sem ambiguidades;
- resultado calculado;
- andamento da revisão.

## 13. Modelo de dados sugerido

Separar inventário calculado de dados persistidos.

### 13.1 Dados calculados

```json
{
  "item_key": "categories:security",
  "module": "categories",
  "compliance_status": "non_compliant",
  "fingerprint": "sha256:...",
  "findings": [
    {
      "rule_id": "category_required_in_selected_scopes",
      "severity": "warning",
      "message_key": "category_missing_in_scope",
      "resource_refs": ["automation:security"]
    }
  ]
}
```

### 13.2 Dados persistidos

```json
{
  "schema_version": 1,
  "modules": {
    "categories": {
      "enabled": true,
      "settings": {
        "scopes": ["automation", "script"]
      }
    }
  },
  "reviews": {
    "categories:security": {
      "review_status": "reviewed",
      "reviewed_fingerprint": "sha256:...",
      "reviewed_at": "2026-08-22T21:30:00Z",
      "note": null
    }
  }
}
```

### 13.3 Armazenamento

- preferir `Store` do Home Assistant com schema versionado;
- usar `ConfigEntry.options` apenas para configurações pequenas e apropriadas ao options flow;
- não persistir cópias completas dos registries;
- não persistir estado volátil de entidades;
- prever migração de schema.

## 14. Arquitetura técnica sugerida

### 14.1 Backend

Custom integration Python responsável por:

- registrar o painel;
- consultar registries e APIs do Home Assistant;
- executar regras determinísticas;
- calcular fingerprints e status;
- armazenar configurações e andamento;
- expor comandos WebSocket próprios;
- validar permissão administrativa.

Comandos conceituais:

```text
ha_organizer/config/get
ha_organizer/config/update
ha_organizer/overview
ha_organizer/module/list
ha_organizer/module/item
ha_organizer/review/set
ha_organizer/scan
```

Os nomes finais podem mudar, mas evitar um endpoint diferente para cada tabela se um contrato genérico por módulo for suficiente.

### 14.2 Frontend

- painel customizado em TypeScript/Lit;
- item próprio na sidebar;
- responsivo para desktop e mobile;
- comunicação por WebSocket;
- componentes próprios ou APIs de frontend documentadas;
- evitar dependência direta de componentes internos não suportados, pois podem mudar entre releases;
- lazy loading das telas e dados sempre que possível.

Referências:

- Custom panels: <https://developers.home-assistant.io/docs/frontend/custom-ui/creating-custom-panels/>
- Extensão WebSocket: <https://developers.home-assistant.io/docs/frontend/extending/websocket-api/>

### 14.3 Atualização dos dados

- executar scan inicial ao abrir o painel;
- permitir atualização manual;
- usar eventos de atualização dos registries quando houver API estável;
- aplicar debounce para evitar várias análises seguidas;
- não reprocessar o inventário inteiro por mudança de estado comum de sensores;
- cache deve ser invalidável e nunca ser a única fonte do inventário.

## 15. UX sugerida

### 15.1 Navegação

```text
Overview
Categories
Areas
Zones
Entity IDs
Exposed & Aliases
Settings
```

### 15.2 Padrão de tela

Cada módulo deve manter uma estrutura consistente:

- título e descrição curta;
- progresso de revisão;
- resumo de conformidade;
- busca e filtros;
- tabela/lista;
- detalhe do item;
- ações somente sobre o workflow do Organizer: revisar, ignorar, reabrir;
- link para o Home Assistant quando possível.

### 15.3 Linguagem

- “Revisado” significa que o usuário conferiu os dados exibidos.
- “Conforme” significa que as regras automáticas foram atendidas.
- “Ignorado” significa uma exceção consciente.
- “Desatualizado” significa que o recurso mudou desde a revisão.
- Não usar “Resolvido” no beta, pois a integração não executa nem necessariamente consegue confirmar a correção pretendida pelo usuário.

## 16. Severidade de findings

| Severidade | Uso |
| --- | --- |
| `error` | Colisão objetiva ou configuração que certamente viola uma regra explícita. |
| `warning` | Divergência relevante e provavelmente não intencional. |
| `info` | Informação útil ou sugestão sem indicação forte de problema. |

Se a conclusão depender do contexto humano, preferir `attention` no item e `warning` ou `info` no finding, em vez de afirmar que existe um erro.

## 17. Segurança e privacidade

- painel e comandos de configuração/revisão disponíveis somente para administradores;
- não enviar inventário para serviços externos;
- não registrar aliases, coordenadas ou nomes de áreas em logs normais;
- sanitizar logs de erro;
- não expor coordenadas completas no Overview;
- nenhuma telemetria no beta;
- nenhuma IA ou API externa.

## 18. Fora do escopo do beta

- alterações automáticas em recursos do Home Assistant;
- correção em lote;
- análise com IA;
- similaridade semântica entre nomes;
- análise completa de dependências de automações e scripts;
- histórico detalhado de todas as revisões;
- colaboração entre múltiplos usuários com atribuição individual;
- importação/exportação de políticas;
- sincronização de regras entre instalações;
- criação de Repairs nativos para cada finding;
- sensores do Organizer para dashboards;

## 19. Critérios de aceite

1. A integração pode ser configurada pela UI e cria um painel acessível na sidebar.
2. O painel só é acessível por administradores.
3. O usuário pode habilitar e desabilitar módulos.
4. Categories compara pelo menos automations e scripts.
5. Areas lista áreas e seus recursos relacionados.
6. Zones lista zonas e executa as verificações determinísticas definidas.
7. Entity IDs valida pelo menos um padrão configurado pelo usuário.
8. Exposed Entities lista entidades expostas, assistentes e aliases.
9. Colisões exatas e normalizadas de nomes/aliases são agrupadas e exibidas.
10. O usuário pode marcar um item como revisado ou ignorado.
11. O progresso continua após reinício do Home Assistant.
12. Uma mudança relevante transforma uma revisão anterior em `stale`.
13. A conformidade calculada não é alterada ao marcar um item como revisado.
14. Nenhuma ação do painel altera recursos nativos do Home Assistant.
15. Todas as tabelas possuem busca e filtros mínimos adequados ao módulo.
16. O frontend funciona em layouts desktop e mobile.
17. Falhas em um módulo não impedem a abertura do restante do painel.

## 20. Estratégia de implementação

Ordem sugerida para reduzir risco:

1. estrutura da integração, config flow, armazenamento e registro do painel;
2. contrato WebSocket genérico e shell do frontend;
3. modelo de regras, findings, fingerprints e revisões;
4. Categories, validando o modelo de comparação e progresso;
5. Areas e Zones;
6. Entity IDs e configuração do padrão;
7. Exposed Entities & Aliases;
8. Overview consolidado;
9. testes, traduções, tratamento de versões e refinamento responsivo.

## 21. Testes mínimos

### Backend

- regras de normalização;
- cálculo determinístico de fingerprints;
- transições `pending`, `reviewed`, `ignored` e `stale`;
- migração e persistência do Store;
- permissões WebSocket;
- categorias presentes e ausentes por escopo;
- áreas sem associação e associações divergentes;
- zonas duplicadas e sobrepostas;
- validação de padrões de `entity_id`;
- agrupamento de colisões entre nome e aliases;
- comportamento quando registries ou APIs opcionais não estão disponíveis.

### Frontend

- loading, vazio e erro por módulo;
- filtros e busca;
- marcação de revisão;
- exibição separada de conformidade e progresso;
- item `stale`;
- responsividade;
- textos traduzíveis.

## 22. Decisões que podem ser refinadas durante a implementação

- versão mínima do Home Assistant suportada;
- sintaxe exata do construtor de padrão de `entity_id`;
- limiar geométrico para considerar zonas praticamente idênticas;
- lista inicial de nomes/aliases genéricos;
- links profundos possíveis para telas nativas;
- virtualização ou paginação das tabelas;
- se itens automaticamente conformes entram no denominador do progresso de revisão.

Para o último ponto, a recomendação inicial é: todos os itens visíveis entram no progresso, mas a UI deve permitir “marcar todos os conformes como revisados” somente dentro do Organizer. Essa ação não altera o Home Assistant e pode ser descartada se complicar o beta.
