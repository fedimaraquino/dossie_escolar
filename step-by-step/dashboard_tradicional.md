# Dashboard Tradicional - Documentação de Implementação

## Data: 09/01/2025
## Arquivo: `templates/dashboard_otimizado.html`

## Visão Geral
Redesenho completo do dashboard para um modelo tradicional e objetivo, focado em funcionalidade e simplicidade visual.

## Estrutura do Dashboard

### 1. Header Simples
```html
<div class="row mb-4">
    <div class="col-12 d-flex justify-content-between align-items-center">
        <h2 class="fw-bold mb-0">
            <i class="fas fa-tachometer-alt me-2 text-primary"></i>Dashboard do Sistema
        </h2>
        <span class="text-muted">{{ current_date.strftime('%d/%m/%Y %H:%M') }}</span>
    </div>
</div>
```
**Função:** Cabeçalho limpo com título e data/hora atual.
**Variáveis necessárias:** `current_date` (datetime)

### 2. Cards de Indicadores (4 cards pequenos)
```html
<div class="row mb-4">
    <div class="col-md-3 col-6 mb-3">
        <!-- Card Dossiês -->
    </div>
    <!-- ... outros cards -->
</div>
```

#### Card 1 - Dossiês
- **Ícone:** `fas fa-folder` (azul)
- **Valor:** `{{ stats.total_dossies or 0 }}`
- **Label:** "Dossiês"

#### Card 2 - Movimentações
- **Ícone:** `fas fa-exchange-alt` (verde)
- **Valor:** `{{ stats.total_movimentacoes or 0 }}`
- **Label:** "Movimentações"

#### Card 3 - Pendências
- **Ícone:** `fas fa-exclamation-triangle` (amarelo)
- **Valor:** `{{ stats.movimentacoes_pendentes or 0 }}`
- **Label:** "Pendências"

#### Card 4 - Usuários Ativos
- **Ícone:** `fas fa-users` (azul claro)
- **Valor:** `{{ stats.usuarios_ativos or 0 }}`
- **Label:** "Usuários Ativos"

**Variáveis necessárias:** `stats` (dict com as chaves acima)

### 3. Tabela de Últimos Dossiês
```html
<div class="col-lg-7 mb-4">
    <div class="card h-100">
        <div class="card-header">
            <i class="fas fa-list me-2 text-primary"></i>Últimos Dossiês Cadastrados
        </div>
        <div class="card-body p-0">
            <table class="table table-sm mb-0">
                <!-- ... estrutura da tabela -->
            </table>
        </div>
    </div>
</div>
```

**Colunas da tabela:**
- Número do dossiê
- Nome do aluno
- Escola
- Status (com badge colorido)
- Data de cadastro

**Variáveis necessárias:** `ultimos_dossies` (lista de objetos Dossie)
**Filtros Jinja necessários:** `situacao_badge`, `situacao_label`

### 4. Gráfico de Movimentações
```html
<div class="col-lg-5 mb-4">
    <div class="card h-100">
        <div class="card-header">
            <i class="fas fa-chart-bar me-2 text-success"></i>Movimentações por Mês
        </div>
        <div class="card-body">
            <canvas id="graficoMovimentacoes"></canvas>
        </div>
    </div>
</div>
```

**Tecnologia:** Chart.js
**Tipo:** Gráfico de barras
**Dados atuais:** Estáticos (exemplo)
**Próximo passo:** Integrar dados reais do backend

### 5. Atalhos Rápidos
```html
<div class="row mb-4">
    <div class="col-12">
        <div class="d-flex gap-2">
            <a href="{{ url_for('dossie.novo') }}" class="btn btn-primary">
                <i class="fas fa-plus me-1"></i>Novo Dossiê
            </a>
            <!-- ... outros botões -->
        </div>
    </div>
</div>
```

**Botões disponíveis:**
- Novo Dossiê (azul)
- Nova Movimentação (verde)
- Novo Solicitante (azul claro)
- Configurações (amarelo)

## Integração com Backend

### Variáveis Necessárias no Contexto

```python
# No controller/rota do dashboard
context = {
    'current_date': datetime.now(),
    'stats': {
        'total_dossies': Dossie.query.count(),
        'total_movimentacoes': Movimentacao.query.count(),
        'movimentacoes_pendentes': Movimentacao.query.filter_by(status='pendente').count(),
        'usuarios_ativos': Usuario.query.filter_by(ativo=True).count()
    },
    'ultimos_dossies': Dossie.query.order_by(Dossie.data_cadastro.desc()).limit(10).all()
}
```

### Filtros Jinja Necessários

```python
# Em app.py ou utils
@app.template_filter('situacao_badge')
def situacao_badge(status):
    badges = {
        'disponivel': 'success',
        'emprestado': 'warning',
        'perdido': 'danger',
        'arquivado': 'secondary'
    }
    return badges.get(status, 'primary')

@app.template_filter('situacao_label')
def situacao_label(status):
    labels = {
        'disponivel': 'Disponível',
        'emprestado': 'Emprestado',
        'perdido': 'Perdido',
        'arquivado': 'Arquivado'
    }
    return labels.get(status, status.title())
```

## Responsividade

- **Desktop:** Cards em linha (4 colunas)
- **Tablet:** Cards em 2x2 (2 colunas)
- **Mobile:** Cards empilhados (1 coluna)
- **Tabela:** Scroll horizontal em telas pequenas
- **Gráfico:** Redimensiona automaticamente

## Próximos Passos Sugeridos

1. **Integração de dados reais:**
   - Conectar gráfico com dados de movimentações por mês
   - Implementar filtros dinâmicos por escola/período

2. **Otimizações:**
   - Cache para estatísticas (Redis/Memcached)
   - Paginação na tabela de dossiês
   - Lazy loading para melhor performance

3. **Funcionalidades adicionais:**
   - Exportação de relatórios
   - Notificações de pendências
   - Filtros avançados

4. **Segurança:**
   - Verificação de permissões por usuário
   - Sanitização de dados
   - Rate limiting

## Arquivos Relacionados

- `templates/base.html` - Template base
- `static/css/style.css` - Estilos customizados
- `static/js/main.js` - JavaScript comum
- `controllers/` - Lógica de negócio
- `models/` - Modelos de dados

## Observações Técnicas

- Uso de Bootstrap 5 para layout responsivo
- FontAwesome para ícones
- Chart.js para gráficos
- Filtros Jinja para formatação
- Estrutura modular e reutilizável 