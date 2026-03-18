function showNotification(message, type) {
    const notificationContainer = document.getElementById('notificationContainer');
    const notificationIcon = notificationContainer.querySelector('.notification-icon');
    const notificationMessage = notificationContainer.querySelector('.notification-message');

    // Set the message text
    notificationMessage.textContent = message;

    // Reset classes
    notificationContainer.classList.remove('success', 'error', 'warning', 'show');
    notificationIcon.className = 'notification-icon bi'; // reset

    // Add the appropriate type class and set icon styles
    if (type === 'success') {
        notificationContainer.classList.add('success');
        notificationIcon.classList.add('bi-check-circle-fill', 'text-success');
    } else if (type === 'error') {
        notificationContainer.classList.add('error');
        notificationIcon.classList.add('bi-x-circle-fill', 'text-danger');
    } else if (type === 'warning') {
        notificationContainer.classList.add('warning');
        notificationIcon.classList.add('bi-exclamation-triangle-fill', 'text-warning');
    }

    // Ajoute la classe show (CSS gère l’animation)
    notificationContainer.classList.add('show');

    // Retire la notif après 3 secondes
    setTimeout(() => {
        notificationContainer.classList.remove('show');
    }, 3000);
}
