document.addEventListener('DOMContentLoaded', function() {
    window.dash_clientside = window.dash_clientside || {};
    var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    window.dash_clientside.timezone = timezone;
});
