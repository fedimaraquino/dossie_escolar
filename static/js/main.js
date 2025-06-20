// Sistema de Controle de Dossiê Escolar - JavaScript Principal

$(document).ready(function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide apenas flash messages após 5 segundos (não alerts informativos)
    setTimeout(function() {
        $('.alert.alert-dismissible').fadeOut('slow');
    }, 5000);

    // Adicionar classe fade-in aos cards
    $('.card').addClass('fade-in');

    // Confirmar ações de exclusão
    $('.btn-delete').on('click', function(e) {
        e.preventDefault();
        var item = $(this).data('item') || 'este item';
        if (confirm('Tem certeza que deseja excluir ' + item + '?\n\nEsta ação não pode ser desfeita.')) {
            // Prosseguir com a exclusão
            var form = $(this).closest('form');
            if (form.length) {
                form.submit();
            } else {
                window.location.href = $(this).attr('href');
            }
        }
    });

    // Busca em tempo real (debounced)
    var searchTimeout;
    $('.search-input').on('input', function() {
        clearTimeout(searchTimeout);
        var searchTerm = $(this).val();
        var targetTable = $(this).data('target') || '.searchable-table';
        
        searchTimeout = setTimeout(function() {
            filterTable(targetTable, searchTerm);
        }, 300);
    });

    // Função para filtrar tabelas
    function filterTable(tableSelector, searchTerm) {
        var table = $(tableSelector);
        var rows = table.find('tbody tr');
        
        if (searchTerm === '') {
            rows.show();
            return;
        }
        
        rows.each(function() {
            var row = $(this);
            var text = row.text().toLowerCase();
            if (text.indexOf(searchTerm.toLowerCase()) > -1) {
                row.show();
            } else {
                row.hide();
            }
        });
    }

    // Validação de formulários
    $('.needs-validation').on('submit', function(e) {
        var form = this;
        if (form.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });

    // Máscara para campos de telefone
    $('.phone-mask').mask('(00) 00000-0000');
    
    // Máscara para CPF
    $('.cpf-mask').mask('000.000.000-00');
    
    // Máscara para CEP
    $('.cep-mask').mask('00000-000');

    // Upload de arquivos com preview
    $('.file-upload').on('change', function() {
        var input = this;
        var preview = $(input).siblings('.file-preview');
        
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            var file = input.files[0];
            
            // Mostrar informações do arquivo
            var fileInfo = '<div class="alert alert-info">';
            fileInfo += '<strong>Arquivo selecionado:</strong> ' + file.name + '<br>';
            fileInfo += '<strong>Tamanho:</strong> ' + formatFileSize(file.size) + '<br>';
            fileInfo += '<strong>Tipo:</strong> ' + file.type;
            fileInfo += '</div>';
            
            preview.html(fileInfo);
            
            // Se for imagem, mostrar preview
            if (file.type.startsWith('image/')) {
                reader.onload = function(e) {
                    var img = '<img src="' + e.target.result + '" class="img-thumbnail mt-2" style="max-width: 200px;">';
                    preview.append(img);
                };
                reader.readAsDataURL(file);
            }
        }
    });

    // Função para formatar tamanho de arquivo
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        var k = 1024;
        var sizes = ['Bytes', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Contador de caracteres para textareas
    $('.char-counter').each(function() {
        var textarea = $(this);
        var maxLength = textarea.attr('maxlength');
        if (maxLength) {
            var counter = $('<small class="text-muted float-end"></small>');
            textarea.after(counter);
            
            function updateCounter() {
                var remaining = maxLength - textarea.val().length;
                counter.text(remaining + ' caracteres restantes');
                if (remaining < 50) {
                    counter.removeClass('text-muted').addClass('text-warning');
                } else {
                    counter.removeClass('text-warning').addClass('text-muted');
                }
            }
            
            textarea.on('input', updateCounter);
            updateCounter();
        }
    });

    // Botão voltar ao topo
    var backToTop = $('<button class="btn btn-primary btn-floating position-fixed" style="bottom: 20px; right: 20px; z-index: 1000; display: none;"><i class="fas fa-arrow-up"></i></button>');
    $('body').append(backToTop);
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTop.fadeIn();
        } else {
            backToTop.fadeOut();
        }
    });
    
    backToTop.click(function() {
        $('html, body').animate({scrollTop: 0}, 600);
    });

    // Confirmação antes de sair da página com formulário modificado
    var formChanged = false;
    $('form input, form textarea, form select').on('change', function() {
        formChanged = true;
    });
    
    $('form').on('submit', function() {
        formChanged = false;
    });
    
    $(window).on('beforeunload', function() {
        if (formChanged) {
            return 'Você tem alterações não salvas. Tem certeza que deseja sair?';
        }
    });

    // Expandir/colapsar seções
    $('.section-toggle').on('click', function() {
        var target = $($(this).data('target'));
        var icon = $(this).find('i');
        
        target.slideToggle();
        icon.toggleClass('fa-chevron-down fa-chevron-up');
    });

    // Copiar texto para clipboard
    $('.copy-to-clipboard').on('click', function() {
        var text = $(this).data('text') || $(this).text();
        navigator.clipboard.writeText(text).then(function() {
            showToast('Texto copiado para a área de transferência!', 'success');
        });
    });

    // Função para mostrar toast notifications
    function showToast(message, type = 'info') {
        var toast = $('<div class="toast align-items-center text-white bg-' + type + ' border-0 position-fixed" style="top: 20px; right: 20px; z-index: 1100;" role="alert">');
        toast.html('<div class="d-flex"><div class="toast-body">' + message + '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>');
        
        $('body').append(toast);
        var bsToast = new bootstrap.Toast(toast[0]);
        bsToast.show();
        
        toast.on('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    // Atualizar timestamp em tempo real
    $('.live-timestamp').each(function() {
        var element = $(this);
        var timestamp = element.data('timestamp');
        if (timestamp) {
            setInterval(function() {
                element.text(timeAgo(new Date(timestamp)));
            }, 60000); // Atualizar a cada minuto
        }
    });

    // Função para calcular tempo decorrido
    function timeAgo(date) {
        var now = new Date();
        var diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'agora mesmo';
        if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutos atrás';
        if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' horas atrás';
        return Math.floor(diffInSeconds / 86400) + ' dias atrás';
    }

    // Lazy loading para imagens
    $('img[data-src]').each(function() {
        var img = $(this);
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var target = $(entry.target);
                    target.attr('src', target.data('src'));
                    target.removeAttr('data-src');
                    observer.unobserve(entry.target);
                }
            });
        });
        observer.observe(this);
    });
});

// Funções globais
window.DossieSystem = {
    // Confirmar exclusão
    confirmDelete: function(message, callback) {
        if (confirm(message || 'Tem certeza que deseja excluir este item?')) {
            if (typeof callback === 'function') {
                callback();
            }
            return true;
        }
        return false;
    },
    
    // Mostrar loading
    showLoading: function(element) {
        var spinner = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>';
        $(element).prepend(spinner).prop('disabled', true);
    },
    
    // Esconder loading
    hideLoading: function(element) {
        $(element).find('.spinner-border').remove();
        $(element).prop('disabled', false);
    },
    
    // Validar formulário
    validateForm: function(formSelector) {
        var form = $(formSelector);
        var isValid = true;
        
        form.find('[required]').each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        return isValid;
    }
};

// Gerenciamento do tema
document.addEventListener('DOMContentLoaded', function() {
    // Verificar tema salvo
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Configurar botão de tema
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Configurar sidebar
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Configurar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configurar popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Configurar dropdowns do Bootstrap
    const dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
    dropdownTriggerList.map(function (dropdownTriggerEl) {
        return new bootstrap.Dropdown(dropdownTriggerEl);
    });

    // Configurar alertas auto-fecháveis
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});

// Função para alternar o tema
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

// Função para atualizar o ícone do tema
function updateThemeIcon(theme) {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'light' 
            ? '<i class="fas fa-moon"></i>' 
            : '<i class="fas fa-sun"></i>';
    }
}

// Função para alternar a sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        if (mainContent) {
            mainContent.classList.toggle('expanded');
        }
    }
}

// Função para mostrar loading
function showLoading() {
    const loading = document.createElement('div');
    loading.className = 'loading-overlay';
    loading.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loading);
}

// Função para esconder loading
function hideLoading() {
    const loading = document.querySelector('.loading-overlay');
    if (loading) {
        loading.remove();
    }
}

// Função para mostrar mensagem de sucesso
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.alert-container').appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Função para mostrar mensagem de erro
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.alert-container').appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Função para confirmar ação
function confirmAction(message) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirmação</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary confirm-btn">Confirmar</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const modalInstance = new bootstrap.Modal(modal);
        
        modal.querySelector('.confirm-btn').addEventListener('click', () => {
            modalInstance.hide();
            resolve(true);
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
            resolve(false);
        });
        
        modalInstance.show();
    });
}

// Função para formatar data
function formatDate(date) {
    return new Date(date).toLocaleDateString('pt-BR');
}

// Função para formatar CPF
function formatCPF(cpf) {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

// Função para formatar CNPJ
function formatCNPJ(cnpj) {
    return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}

// Função para formatar telefone
function formatPhone(phone) {
    return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
}

// Função para validar email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Função para validar CPF
function validateCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');
    
    if (cpf.length !== 11) return false;
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validação do primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let rev = 11 - (sum % 11);
    if (rev === 10 || rev === 11) rev = 0;
    if (rev !== parseInt(cpf.charAt(9))) return false;
    
    // Validação do segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    rev = 11 - (sum % 11);
    if (rev === 10 || rev === 11) rev = 0;
    if (rev !== parseInt(cpf.charAt(10))) return false;
    
    return true;
}

// Função para validar CNPJ
function validateCNPJ(cnpj) {
    cnpj = cnpj.replace(/[^\d]/g, '');
    
    if (cnpj.length !== 14) return false;
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1{13}$/.test(cnpj)) return false;
    
    // Validação do primeiro dígito verificador
    let size = cnpj.length - 2;
    let numbers = cnpj.substring(0, size);
    let digits = cnpj.substring(size);
    let sum = 0;
    let pos = size - 7;
    
    for (let i = size; i >= 1; i--) {
        sum += numbers.charAt(size - i) * pos--;
        if (pos < 2) pos = 9;
    }
    
    let result = sum % 11 < 2 ? 0 : 11 - sum % 11;
    if (result !== parseInt(digits.charAt(0))) return false;
    
    // Validação do segundo dígito verificador
    size = size + 1;
    numbers = cnpj.substring(0, size);
    sum = 0;
    pos = size - 7;
    
    for (let i = size; i >= 1; i--) {
        sum += numbers.charAt(size - i) * pos--;
        if (pos < 2) pos = 9;
    }
    
    result = sum % 11 < 2 ? 0 : 11 - sum % 11;
    if (result !== parseInt(digits.charAt(1))) return false;
    
    return true;
}

// Controle do menu lateral
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const body = document.body;

    // Função para alternar o menu
    function toggleSidebar() {
        sidebar.classList.toggle('collapsed');
        body.classList.toggle('sidebar-collapsed');
    }

    // Evento de clique no botão de toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Ajustar menu em telas pequenas
    function handleResize() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
            body.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('collapsed');
            body.classList.remove('sidebar-collapsed');
        }
    }

    // Evento de redimensionamento
    window.addEventListener('resize', handleResize);
    handleResize();

    // Fechar menu ao clicar fora em telas pequenas
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(event.target) && 
            !sidebarToggle.contains(event.target) && 
            !sidebar.classList.contains('collapsed')) {
            toggleSidebar();
        }
    });
});
