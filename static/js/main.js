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

    // Auto-hide alerts após 5 segundos
    setTimeout(function() {
        $('.alert').fadeOut('slow');
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
