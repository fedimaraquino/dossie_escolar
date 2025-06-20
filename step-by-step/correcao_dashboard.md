# Correção do Dashboard - Dados da Escola Atual

## Data: 09/01/2025
## Problema: Dashboard mostrando dados incorretos

## Problemas Identificados

### 1. Campo Incorreto no Filtro
- **Problema:** Dashboard usando `Dossie.escola_id` em vez de `Dossie.id_escola`
- **Impacto:** Consultas não retornavam dados corretos da escola selecionada
- **Solução:** Corrigido todos os filtros para usar `Dossie.id_escola`

### 2. Dados Simulados nos Gráficos
- **Problema:** Gráficos usando dados estáticos/fictícios
- **Impacto:** Informações não refletiam a realidade da escola
- **Solução:** Implementado consultas reais para gerar dados dos gráficos

### 3. Falta de Filtro por Escola Atual
- **Problema:** Admin geral não via dados específicos da escola selecionada
- **Impacto:** Dashboard mostrava dados globais em vez de dados da escola atual
- **Solução:** Implementado filtro baseado em `escola_atual_id` da sessão

## Correções Aplicadas

### 1. Arquivo: `app.py` - Rota do Dashboard

#### Antes:
```python
# Usando campo incorreto
'total_dossies': Dossie.query.filter_by(escola_id=escola_atual_id).count(),
'total_movimentacoes': Movimentacao.query.join(Dossie).filter(Dossie.escola_id == escola_atual_id).count(),

# Dados simulados
stats['dossies_por_mes'] = [
    {'mes': 'Nov/2024', 'count': max(1, stats['total_dossies'] // 4)},
    {'mes': 'Dez/2024', 'count': max(1, stats['total_dossies'] // 3)},
    {'mes': 'Jan/2025', 'count': stats['dossies_mes_atual']}
]
```

#### Depois:
```python
# Usando campo correto
'total_dossies': Dossie.query.filter_by(id_escola=escola_atual_id).count(),
'total_movimentacoes': Movimentacao.query.join(Dossie).filter(Dossie.id_escola == escola_atual_id).count(),

# Dados reais dos últimos 3 meses
dossies_por_mes = []
for i in range(3):
    mes_inicio = (hoje.replace(day=1) - timedelta(days=i*30)).replace(day=1)
    mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    if escola_atual_id:
        count = Dossie.query.filter(
            Dossie.id_escola == escola_atual_id,
            Dossie.dt_cadastro >= mes_inicio,
            Dossie.dt_cadastro <= mes_fim
        ).count()
    
    dossies_por_mes.insert(0, {
        'mes': mes_inicio.strftime('%b/%Y'),
        'count': count
    })
```

### 2. Arquivo: `templates/dashboard_corrigido.html`

#### Melhorias Implementadas:
- **Indicador de escola atual:** Mostra qual escola está selecionada (para admin geral)
- **Dados reais nos gráficos:** Gráfico de barras com dados reais dos últimos 3 meses
- **Tabela de últimos dossiês:** Filtrada pela escola atual
- **Cards corretos:** Todos os indicadores filtrados pela escola selecionada

#### Estrutura do Template:
```html
<!-- Informação da escola atual -->
{% if usuario.is_admin_geral() and session.get('escola_atual_id') %}
<div class="alert alert-info">
    <strong>Escola Atual:</strong> {{ session.get('escola_nome', 'Escola selecionada') }}
    <a href="{{ url_for('usuario.trocar_escola') }}" class="btn btn-sm btn-outline-info ms-2">
        <i class="fas fa-exchange-alt me-1"></i>Trocar Escola
    </a>
</div>
{% endif %}

<!-- Cards com dados corretos -->
<div class="fw-bold fs-4">{{ stats.total_dossies or 0 }}</div>

<!-- Gráfico com dados reais -->
<script>
var dados = {{ stats.dossies_por_mes | tojson }};
// Gráfico Chart.js com dados reais
</script>
```

## Resultados Esperados

### Para Admin Geral:
- **Escola não selecionada:** Dashboard mostra dados globais do sistema
- **Escola selecionada:** Dashboard mostra apenas dados da escola escolhida
- **Indicador visual:** Alert mostrando qual escola está ativa

### Para Usuários Comuns:
- **Dados específicos:** Dashboard mostra apenas dados da escola do usuário
- **Performance:** Consultas otimizadas e rápidas

### Cards Corrigidos:
- **Dossiês:** Total de dossiês da escola atual
- **Movimentações:** Total de movimentações da escola atual
- **Pendências:** Movimentações pendentes da escola atual
- **Usuários Ativos:** Usuários ativos da escola atual

### Gráfico Corrigido:
- **Dados reais:** Últimos 3 meses de dossiês cadastrados
- **Filtro por escola:** Apenas dados da escola atual
- **Formato:** Gráfico de barras com Chart.js

## Próximos Passos

1. **Testar dashboard:** Verificar se os dados estão corretos para cada escola
2. **Otimizar consultas:** Considerar cache para melhorar performance
3. **Adicionar mais gráficos:** Movimentações por tipo, status de dossiês, etc.
4. **Implementar filtros:** Permitir seleção de período nos gráficos

## Arquivos Modificados

- `app.py` - Rota do dashboard corrigida
- `templates/dashboard_corrigido.html` - Novo template sem erros
- `controllers/dossie_controller.py` - Filtros corrigidos (anteriormente)

## Observações Técnicas

- **Campo correto:** Sempre usar `id_escola` para filtros de dossiê
- **Sessão:** `escola_atual_id` controla qual escola está ativa para admin geral
- **Performance:** Consultas otimizadas com JOINs quando necessário
- **JavaScript:** Template corrigido para evitar erros de sintaxe 