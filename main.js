document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            try { new bootstrap.Alert(alert).close(); } catch (e) {}
        }, 4500);
    });

    const path = window.location.pathname;
    document.querySelectorAll('.sidebar a').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '/' && path.startsWith(href)) {
            link.classList.add('active');
        }
    });

    document.querySelectorAll('.format-number').forEach(function (el) {
        const v = parseInt(el.textContent.replace(/,/g, ''), 10);
        if (!isNaN(v)) el.textContent = v.toLocaleString();
    });
});

function formatCurrency(value) {
    return '$' + parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2, maximumFractionDigits: 2
    });
}
function formatNumber(value) {
    return parseInt(value, 10).toLocaleString('en-US');
}