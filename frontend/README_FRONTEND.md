# SAFEpass — Frontend do Desafio 01

## Escopo desta entrega

- Landing page pública e responsiva.
- Header global, logo oficial, login/cadastro e modais previstos no layout.
- Planos Free, Aura e Aura+ com CTAs para cadastro/contratação demonstrativa.
- Avaliações e depoimentos da plataforma.
- FAQ e Termos de Uso.
- Painel administrativo para perfil `admin`: visão geral, avaliações, indicações, planos, cupons, campanhas e parcerias.
- A página `/painel` é apenas um encaminhamento para o Meu Dashboard do Desafio 02; não recria esse módulo.

## Correções da revisão da Juliana

- Imagem principal substituída por uma imagem local que comunica cuidado e proteção familiar (`public/images/family-care.webp`).
- Logo oficial do manual aplicado no header e no footer (`public/brand/`).
- CTAs dos cards de perfil alinhados na parte inferior.
- Cards mantêm hover com mudança de cor e elevação.
- Faixa de indicadores ocupa toda a largura da tela. Quando a API ainda não está disponível, mostra os números do layout como **ilustrativos** e identifica essa condição.
- Espaçamento do título da jornada e da seção de depoimentos ampliado.
- Ícone de moeda nos multiplicadores de pontuação e fonte de marca nos valores dos planos.
- Estrelas do rodapé preenchidas em amarelo.
- Menu de conta distingue usuário e administrador; o admin recebe acesso direto ao `/admin`.
- Formulário de avaliação reinicia ao ser aberto novamente e mantém a nota escolhida na estrela do rodapé.

## Fontes

- Corpo: **Inter** (mantida da implementação que recebeu aprovação na revisão).
- Títulos: **Yanone Kaffeesatz**.
- Números e valores destacados: **Days One** como família digital de marca.

As fontes são carregadas de Google Fonts pelo CSS. O PDF da marca contém referências às famílias Days e Yanone Kaffeesatz; confirme com a equipe de identidade visual se `Days One` é a variante exata desejada para todos os valores antes da padronização institucional.

## Painel administrativo — modo de prévia

As telas de cupons, campanhas e parcerias incluem formulários, busca, anexos de exemplo e remoção local de registros para validar a experiência. **Essas telas não persistem dados**: a conexão com API, upload real e PostgreSQL está intencionalmente pendente, pois o backend e o banco serão trabalhados em uma etapa posterior. A autorização real dessas rotas também deve ser validada pelo backend.

## Variáveis de ambiente do frontend

Copie `.env.example` para `.env.local` e defina:

- `API_URL`: URL da API FastAPI usada pelo proxy do Next.
- `NEXT_PUBLIC_API_BASE`: base das chamadas feitas pelo navegador.
- `NEXT_PUBLIC_D02_DASHBOARD_URL`: URL do Meu Dashboard do Desafio 02 (quando o outro squad informar).
- `NEXT_PUBLIC_RESIDENCIA_URL`: link público do programa de Residência Tecnológica, quando a equipe definir.

## Executar

```bash
pnpm install
pnpm dev
```

A aplicação abre em `http://localhost:3000`. Para validar a produção: `pnpm lint`, `pnpm typecheck`, `pnpm test` e `pnpm build`. A API precisa estar disponível para login real, planos, avaliações, indicações e indicadores reais.
