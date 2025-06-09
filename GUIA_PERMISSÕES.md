# 🔐 GUIA COMPLETO - SISTEMA DE PERMISSÕES

## 📍 **ONDE CONFIGURAR PERMISSÕES:**

### **1. Interface Web (Recomendado):**
```
URL: http://localhost:5000/permissoes/perfis
Acesso: Apenas Administrador Geral
```

### **2. Via Código (Programático):**
```python
# No arquivo models/perfil.py
# Métodos: has_permission(), can_create(), can_edit(), etc.
```

### **3. Via Banco de Dados:**
```sql
-- Tabelas: permissoes, perfil_permissoes
-- Relacionamento: perfil -> perfil_permissoes -> permissoes
```

---

## 🎯 **COMO FUNCIONA:**

### **Estrutura:**
1. **Perfis** - Administrador Geral, Admin Escola, Operador, Consulta
2. **Permissões** - Combinação de Módulo + Ação
3. **Relacionamento** - Cada perfil tem N permissões

### **Módulos Disponíveis:**
- `usuario` - Gerenciamento de usuários
- `escola` - Gerenciamento de escolas
- `diretor` - Gerenciamento de diretores
- `dossie` - Gerenciamento de dossiês
- `anexo` - Gerenciamento de anexos
- `movimentacao` - Movimentações de dossiês
- `relatorio` - Relatórios do sistema
- `admin` - Administração do sistema
- `perfil` - Gerenciamento de perfis

### **Ações Disponíveis:**
- `criar` - Criar novos registros
- `editar` - Editar registros existentes
- `excluir` - Excluir registros
- `visualizar` - Visualizar registros
- `total` - Acesso total (admin)

---

## 🛠️ **CONFIGURAÇÃO PRÁTICA:**

### **1. Acessar Interface de Permissões:**
```
1. Login como Administrador Geral
2. Ir para: http://localhost:5000/permissoes/perfis
3. Selecionar perfil na lateral esquerda
4. Marcar/desmarcar permissões desejadas
5. Clicar "Salvar Permissões"
```

### **2. Permissões Padrão por Perfil:**

#### **🔴 Administrador Geral:**
- ✅ **TODAS as permissões** (automático)
- ✅ Acesso total ao sistema
- ✅ Não pode ser editado

#### **🟡 Administrador da Escola:**
- ✅ Usuários: criar, editar, visualizar (da escola)
- ✅ Dossiês: criar, editar, excluir, visualizar
- ✅ Anexos: criar, editar, excluir, visualizar
- ✅ Movimentações: criar, editar, visualizar
- ✅ Relatórios: da escola
- ✅ Escola: visualizar

#### **🟢 Operador:**
- ✅ Dossiês: criar, editar, visualizar
- ✅ Anexos: criar, editar, visualizar
- ✅ Movimentações: criar, visualizar
- ✅ Usuários: visualizar
- ✅ Escola: visualizar

#### **🔵 Consulta:**
- ✅ Dossiês: visualizar
- ✅ Anexos: visualizar
- ✅ Movimentações: visualizar
- ✅ Usuários: visualizar
- ✅ Escola: visualizar

---

## 💻 **USO NO CÓDIGO:**

### **1. Decorator para Rotas:**
```python
from utils.permissions import require_permission

@app.route('/dossies/criar')
@require_permission('dossie', 'criar')
def criar_dossie():
    # Só usuários com permissão podem acessar
    return render_template('dossie/criar.html')
```

### **2. Verificação Manual:**
```python
from utils.permissions import has_permission

def minha_funcao():
    usuario = Usuario.query.get(session['user_id'])
    
    if has_permission(usuario, 'dossie', 'editar'):
        # Usuário pode editar dossiês
        pass
    else:
        # Usuário não tem permissão
        flash('Acesso negado', 'error')
```

### **3. Verificação em Templates:**
```html
<!-- Mostrar botão apenas se tiver permissão -->
{% if usuario.perfil_obj.has_permission('dossie', 'criar') %}
    <a href="/dossies/criar" class="btn btn-primary">Criar Dossiê</a>
{% endif %}
```

### **4. Constantes para Facilitar:**
```python
from utils.permissions import Modulos, Acoes

# Em vez de strings, use constantes
@require_permission(Modulos.DOSSIE, Acoes.CRIAR)
def criar_dossie():
    pass
```

---

## 🔧 **EXEMPLOS PRÁTICOS:**

### **Cenário 1: Novo Perfil "Secretário"**
```python
# 1. Criar perfil no banco
perfil = Perfil(perfil='Secretário', descricao='Secretário da escola')
db.session.add(perfil)
db.session.commit()

# 2. Configurar permissões via interface web
# Ou programaticamente:
permissoes = ['dossie_visualizar', 'usuario_visualizar', 'escola_visualizar']
for perm_nome in permissoes:
    permissao = Permissao.query.filter_by(nome=perm_nome).first()
    pp = PerfilPermissao(perfil_id=perfil.id_perfil, permissao_id=permissao.id)
    db.session.add(pp)
db.session.commit()
```

### **Cenário 2: Restringir Acesso a Relatórios**
```python
@app.route('/relatorios')
@require_permission('relatorio', 'visualizar')
def relatorios():
    # Só quem tem permissão de relatório acessa
    return render_template('relatorios/index.html')
```

### **Cenário 3: Verificar Permissão Dinamicamente**
```python
def pode_editar_dossie(usuario, dossie):
    # Verificar permissão básica
    if not has_permission(usuario, 'dossie', 'editar'):
        return False
    
    # Verificar se é da mesma escola
    if not check_escola_access(usuario, dossie.escola_id):
        return False
    
    return True
```

---

## 📊 **COMANDOS ÚTEIS:**

### **Ver Permissões de um Usuário:**
```python
python manage.py shell

# No shell:
usuario = Usuario.query.filter_by(email='admin@escola.com').first()
permissoes = usuario.perfil_obj.get_permissoes()
for p in permissoes:
    print(f"{p.modulo}.{p.acao} - {p.descricao}")
```

### **Criar Nova Permissão:**
```python
# Via código
permissao = Permissao(
    nome='dossie_arquivar',
    descricao='Arquivar dossiês',
    modulo='dossie',
    acao='arquivar'
)
db.session.add(permissao)
db.session.commit()
```

### **Atribuir Permissão a Perfil:**
```python
perfil = Perfil.query.filter_by(perfil='Operador').first()
permissao = Permissao.query.filter_by(nome='dossie_arquivar').first()

pp = PerfilPermissao(perfil_id=perfil.id_perfil, permissao_id=permissao.id)
db.session.add(pp)
db.session.commit()
```

---

## 🎯 **RESUMO:**

### **✅ O QUE VOCÊ PODE FAZER:**
1. **Configurar permissões** via interface web
2. **Criar novos perfis** com permissões específicas
3. **Proteger rotas** com decorators
4. **Verificar permissões** no código
5. **Personalizar acesso** por módulo e ação

### **📍 ONDE CONFIGURAR:**
- **Interface Web:** `/permissoes/perfis`
- **Código:** `models/perfil.py` e `utils/permissions.py`
- **Banco:** Tabelas `permissoes` e `perfil_permissoes`

### **🔐 SEGURANÇA:**
- **Admin Geral** sempre tem acesso total
- **Verificação automática** em rotas protegidas
- **Controle granular** por módulo e ação
- **Isolamento por escola** para não-admins

**Agora você tem controle total sobre quem pode fazer o quê no sistema!** 🚀
