# Instruções de desenvolvimento do HA Organizer

## Fluxo de trabalho durante o MVP

- Durante a fase de testes exploratórios do MVP, não executar automaticamente a suíte de testes, testes unitários, lint ou validações equivalentes, salvo solicitação explícita do usuário.
- Consultar sempre o arquivo `TODO.md` na raiz antes de iniciar uma nova tarefa. Os itens desse arquivo fazem parte do escopo prioritário de ajustes.
- Para investigar falhas encontradas durante os testes locais do usuário, consultar o log do Home Assistant em:
  `/home/alves-dev/projects/others/core/config/home-assistant.log`
- Não alterar o projeto de referência em `/home/alves-dev/projects/python/ia-usage`.
- Alterações devem permanecer neste repositório, exceto quando o usuário solicitar explicitamente uma operação de cópia ou implantação.

## Decisões registradas do MVP

- O projeto é uma custom integration para Home Assistant `2026.8.0`; a dependência e o formato de versão devem permanecer alinhados com essa versão durante o MVP.
- A integração é somente leitura em relação aos dados do Home Assistant: ela audita e registra revisões, mas não renomeia entidades, áreas, zonas, labels ou categorias.
- A instalação da integração usa um fluxo mínimo. As políticas são configuradas depois, na página `Settings`.
- A interface deve ser apresentada em inglês inicialmente. A tradução atual acontece na camada da UI; nomes e dados do usuário não devem ser traduzidos.
- Os módulos atuais são Overview, Categories, Areas, Zones, Labels, Entity IDs e Exposed & Aliases.
- Categories compara automações e scripts com uma única opção `compare`. Quando habilitada, compara também os ícones; quando desabilitada, os escopos permanecem independentes.
- Cada módulo possui sua própria política de normalização. Não reintroduzir uma seção de normalização compartilhada.
- Entity IDs usam a política que o usuário cola em Settings, inspirada nos tokens configuráveis do Home Assistant (`area`, `device`, `entity` e eventualmente `floor`). O Home Assistant não oferece uma política global simples para ser lida como configuração do Organizer.
- Labels são obtidos pelo `label_registry` e possuem atalho para `/config/labels`.
- Areas, Zones e entidades expostas possuem atalhos para as telas nativas do Home Assistant:
  - Areas: `/config/areas/dashboard`
  - Zones: `/config/zone`
  - Exposed: `/config/voice-assistants/expose`
- Entidades expostas devem ser consultadas pela API interna de exposição do Home Assistant (`DATA_EXPOSED_ENTITIES`, `KNOWN_ASSISTANTS` e `async_should_expose`), incluindo configurações do Entity Registry.
- O conceito de ícone ativo durante os testes é o número 2, salvo em `custom_components/ha_organizer/icon.png`; os demais conceitos ficam em `examples/icons/` como referência.
- O painel serve o ícone por `/ha_organizer/icon.png` e a cópia para o ambiente local deve ser feita com `.dev/copy-to-core.sh`.
- Links nativos de edição devem permanecer como links simples para as rotas do Home Assistant e não devem tentar editar dados por WebSocket do Organizer.

## Encerramento e publicação

- Antes de qualquer nova tarefa, ler `TODO.md`, mesmo que ele permaneça ignorado pelo Git para não misturar planejamento local ao produto publicado.
- Antes de commit público, revisar arquivos locais, caches, IDE metadata, logs, `.env`, credenciais e caminhos específicos da máquina. Os PNGs em `examples/icons/` e o ícone ativo são assets intencionais e podem ser publicados.
- O branch principal é `main` e o remoto é `origin` apontando para `git@github.com:alves-dev/ha-organizer.git`.
- Não fazer commit ou push automaticamente durante os testes exploratórios; somente fazê-lo quando o usuário pedir explicitamente.

## Referências de produto e UX

Usar como inspiração para auditoria, inventário, agrupamento de findings, filtros e experiência de manutenção:

- https://github.com/TheIcelandicguy/entity-manager
- https://github.com/Franz646/orphan-cleaner
- https://github.com/MacSiem/ha-config-auditor
- https://github.com/dummylabs/thewatchman
- https://github.com/frenck/spook
- https://spook.boo/
- https://github.com/skjall/home-assistant-entity-manager
