// Script principal de la plateforme des Coopératives Agricoles.

document.addEventListener('DOMContentLoaded', function () {

    // --- Mode sombre du panneau d'administration (mémorisé) ---
    var toggle = document.getElementById('themeToggle');
    function appliquerTheme(sombre) {
        document.body.classList.toggle('dark-admin', sombre);
        var ic = document.getElementById('themeIcon');
        var lb = document.getElementById('themeLabel');
        if (ic) ic.textContent = sombre ? '☀️' : '🌙';
        if (lb) lb.textContent = sombre ? 'Mode clair' : 'Mode sombre';
    }
    if (toggle) {
        var memo = false;
        try { memo = localStorage.getItem('admin-theme') === 'dark'; } catch (e) {}
        appliquerTheme(memo);
        toggle.addEventListener('click', function () {
            var sombre = !document.body.classList.contains('dark-admin');
            appliquerTheme(sombre);
            try { localStorage.setItem('admin-theme', sombre ? 'dark' : 'light'); } catch (e) {}
        });
    }

    // --- Toasts : disparition automatique après 4 secondes ---
    document.querySelectorAll('.toast-msg').forEach(function (t) {
        setTimeout(function () {
            t.style.transition = 'opacity .4s ease';
            t.style.opacity = '0';
            setTimeout(function () { t.remove(); }, 400);
        }, 4000);
    });

    // --- Modale de confirmation pour les actions sensibles ---
    // Sur un <form data-confirm="message">, on intercepte l'envoi
    // et on demande confirmation via la modale Bootstrap.
    var modalEl = document.getElementById('confirmModal');
    if (modalEl && window.bootstrap) {
        var modal = new bootstrap.Modal(modalEl);
        var formEnAttente = null;

        document.querySelectorAll('form[data-confirm]').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                if (form.dataset.confirmed === 'true') return; // déjà confirmé
                e.preventDefault();
                formEnAttente = form;
                document.getElementById('confirmTexte').textContent = form.dataset.confirm;
                modal.show();
            });
        });

        document.getElementById('confirmOui').addEventListener('click', function () {
            if (formEnAttente) {
                formEnAttente.dataset.confirmed = 'true';
                formEnAttente.submit();
            }
            modal.hide();
        });
    }
});
