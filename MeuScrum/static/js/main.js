// MeuScrum - JavaScript Global

// Utility function to show alerts
function showAlert(message, type = 'info', containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }
}

// Format date to Brazilian format
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Get status class for styling
function getStatusClass(status) {
    if (status === 'Concluída' || status === 'Concluído') return 'completed';
    if (status === 'Cancelada' || status === 'Pausado') return 'paused';
    return 'active';
}

