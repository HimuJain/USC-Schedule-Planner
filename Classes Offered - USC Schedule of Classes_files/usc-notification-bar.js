if( document.readyState !== 'loading' ) {
    usc_notification_bar_setup();
} else {
    document.addEventListener( 'DOMContentLoaded', function() {
        usc_notification_bar_setup();
    });
}

function usc_notification_bar_setup() {
    const notificationBar = document.querySelector('.notification-bar');
    if ( null !== notificationBar ) {
        document.body.insertBefore(notificationBar, document.body.firstChild);
        notificationBar.classList.add('show');
        notificationBar.setAttribute('role', 'status');
        notificationBar.setAttribute('aria-live', 'polite');
    }
}

