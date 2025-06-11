# utils/validators.py
"""
Validadores rigorosos para entrada de dados
"""

import re
import html
from datetime import datetime

class ValidationError(Exception):
    """Exceção para erros de validação"""
    pass

def sanitizar_string(texto, max_length=None):
    """
    Sanitiza string removendo caracteres perigosos
    
    Args:
        texto (str): Texto a ser sanitizado
        max_length (int): Tamanho máximo permitido
        
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return ""
    
    # Converter para string se não for
    texto = str(texto).strip()
    
    # Escapar HTML para prevenir XSS
    texto = html.escape(texto)
    
    # Remover caracteres de controle
    texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
    
    # Limitar tamanho se especificado
    if max_length and len(texto) > max_length:
        texto = texto[:max_length]
    
    return texto

def validar_email(email):
    """
    Valida formato de email
    
    Args:
        email (str): Email a ser validado
        
    Returns:
        str: Email sanitizado e validado
        
    Raises:
        ValidationError: Se email inválido
    """
    if not email:
        raise ValidationError("Email é obrigatório")
    
    email = sanitizar_string(email, 120).lower()
    
    # Regex para validação de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Formato de email inválido")
    
    # Verificar domínios suspeitos
    dominios_bloqueados = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
    dominio = email.split('@')[1]
    
    if dominio in dominios_bloqueados:
        raise ValidationError("Domínio de email não permitido")
    
    return email

def validar_cpf(cpf):
    """
    Valida CPF brasileiro
    
    Args:
        cpf (str): CPF a ser validado
        
    Returns:
        str: CPF formatado (apenas números)
        
    Raises:
        ValidationError: Se CPF inválido
    """
    if not cpf:
        return None
    
    # Remover formatação
    cpf = re.sub(r'[^\d]', '', str(cpf))
    
    # Verificar tamanho
    if len(cpf) != 11:
        raise ValidationError("CPF deve ter 11 dígitos")
    
    # Verificar se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido")
    
    # Validar dígitos verificadores
    def calcular_digito(cpf_parcial, peso_inicial):
        soma = sum(int(cpf_parcial[i]) * (peso_inicial - i) for i in range(len(cpf_parcial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito
    if int(cpf[9]) != calcular_digito(cpf[:9], 10):
        raise ValidationError("CPF inválido")
    
    # Segundo dígito
    if int(cpf[10]) != calcular_digito(cpf[:10], 11):
        raise ValidationError("CPF inválido")
    
    return cpf

def validar_telefone(telefone):
    """
    Valida telefone brasileiro
    
    Args:
        telefone (str): Telefone a ser validado
        
    Returns:
        str: Telefone formatado (apenas números)
        
    Raises:
        ValidationError: Se telefone inválido
    """
    if not telefone:
        return None
    
    # Remover formatação
    telefone = re.sub(r'[^\d]', '', str(telefone))
    
    # Verificar tamanho (10 ou 11 dígitos)
    if len(telefone) not in [10, 11]:
        raise ValidationError("Telefone deve ter 10 ou 11 dígitos")
    
    # Verificar se começa com código de área válido
    if not telefone.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19',  # SP
                               '21', '22', '24',  # RJ
                               '27', '28',  # ES
                               '31', '32', '33', '34', '35', '37', '38',  # MG
                               '41', '42', '43', '44', '45', '46',  # PR
                               '47', '48', '49',  # SC
                               '51', '53', '54', '55',  # RS
                               '61',  # DF
                               '62', '64',  # GO
                               '63',  # TO
                               '65', '66',  # MT
                               '67',  # MS
                               '68',  # AC
                               '69',  # RO
                               '71', '73', '74', '75', '77',  # BA
                               '79',  # SE
                               '81', '87',  # PE
                               '82',  # AL
                               '83',  # PB
                               '84',  # RN
                               '85', '88',  # CE
                               '86', '89',  # PI
                               '91', '93', '94',  # PA
                               '92', '97',  # AM
                               '95',  # RR
                               '96',  # AP
                               '98', '99')):  # MA
        raise ValidationError("Código de área inválido")
    
    return telefone

def validar_nome(nome):
    """
    Valida nome de pessoa
    
    Args:
        nome (str): Nome a ser validado
        
    Returns:
        str: Nome sanitizado
        
    Raises:
        ValidationError: Se nome inválido
    """
    if not nome:
        raise ValidationError("Nome é obrigatório")
    
    nome = sanitizar_string(nome, 100)
    
    # Verificar tamanho mínimo
    if len(nome) < 2:
        raise ValidationError("Nome deve ter pelo menos 2 caracteres")
    
    # Verificar se contém apenas letras, espaços e acentos
    if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', nome):
        raise ValidationError("Nome deve conter apenas letras e espaços")
    
    # Verificar se tem pelo menos um espaço (nome e sobrenome)
    if ' ' not in nome.strip():
        raise ValidationError("Informe nome e sobrenome")
    
    return nome.title()  # Capitalizar

def validar_senha(senha):
    """
    Valida força da senha
    
    Args:
        senha (str): Senha a ser validada
        
    Returns:
        str: Senha validada
        
    Raises:
        ValidationError: Se senha inválida
    """
    if not senha:
        raise ValidationError("Senha é obrigatória")
    
    if len(senha) < 8:
        raise ValidationError("Senha deve ter pelo menos 8 caracteres")
    
    if len(senha) > 128:
        raise ValidationError("Senha muito longa (máximo 128 caracteres)")
    
    # Verificar complexidade
    tem_maiuscula = bool(re.search(r'[A-Z]', senha))
    tem_minuscula = bool(re.search(r'[a-z]', senha))
    tem_numero = bool(re.search(r'\d', senha))
    tem_especial = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', senha))
    
    if not tem_maiuscula:
        raise ValidationError("Senha deve ter pelo menos uma letra maiúscula")
    
    if not tem_minuscula:
        raise ValidationError("Senha deve ter pelo menos uma letra minúscula")
    
    if not tem_numero:
        raise ValidationError("Senha deve ter pelo menos um número")
    
    if not tem_especial:
        raise ValidationError("Senha deve ter pelo menos um caractere especial")
    
    # Verificar senhas comuns
    senhas_fracas = [
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey',
        'dragon', 'master', 'shadow', 'superman', 'michael'
    ]
    
    if senha.lower() in senhas_fracas:
        raise ValidationError("Senha muito comum, escolha uma mais segura")
    
    return senha

def validar_data_nascimento(data_str):
    """
    Valida data de nascimento
    
    Args:
        data_str (str): Data no formato DD/MM/AAAA
        
    Returns:
        datetime.date: Data validada
        
    Raises:
        ValidationError: Se data inválida
    """
    if not data_str:
        return None
    
    try:
        # Tentar diferentes formatos
        formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        data = None
        
        for formato in formatos:
            try:
                data = datetime.strptime(data_str, formato).date()
                break
            except ValueError:
                continue
        
        if not data:
            raise ValidationError("Formato de data inválido (use DD/MM/AAAA)")
        
        # Verificar se a data é razoável
        hoje = datetime.now().date()
        idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
        
        if idade < 0:
            raise ValidationError("Data de nascimento não pode ser no futuro")
        
        if idade > 120:
            raise ValidationError("Data de nascimento muito antiga")
        
        return data
        
    except ValueError as e:
        raise ValidationError(f"Data inválida: {e}")

def validar_dados_usuario(dados):
    """
    Valida todos os dados de um usuário
    
    Args:
        dados (dict): Dicionário com dados do usuário
        
    Returns:
        dict: Dados validados e sanitizados
        
    Raises:
        ValidationError: Se algum dado for inválido
    """
    dados_validados = {}
    
    # Validar campos obrigatórios
    dados_validados['nome'] = validar_nome(dados.get('nome'))
    dados_validados['email'] = validar_email(dados.get('email'))
    
    # Validar campos opcionais
    if dados.get('cpf'):
        dados_validados['cpf'] = validar_cpf(dados.get('cpf'))
    
    if dados.get('telefone'):
        dados_validados['telefone'] = validar_telefone(dados.get('telefone'))
    
    if dados.get('data_nascimento'):
        dados_validados['data_nascimento'] = validar_data_nascimento(dados.get('data_nascimento'))
    
    # Sanitizar outros campos
    if dados.get('endereco'):
        dados_validados['endereco'] = sanitizar_string(dados.get('endereco'), 200)
    
    if dados.get('cargo'):
        dados_validados['cargo'] = sanitizar_string(dados.get('cargo'), 100)
    
    return dados_validados
