from flask_assets import Bundle

app_css = Bundle('app.scss', filters='scss', output='styles/app.css')

app_js = Bundle('app.js', filters='jsmin', output='scripts/app.js')

vendor_css = Bundle(
    'vendor/semantic.min.css',
    'https://cdn.rawgit.com/mdehoog/Semantic-UI-Calendar/76959c6f7d33a527b49be76789e984a0a407350b/dist/calendar.min.css',
    output='styles/vendor.css')

vendor_js = Bundle(
    'https://code.jquery.com/jquery-3.3.1.js',
    'https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js',
    'https://cdn.datatables.net/1.10.19/js/dataTables.semanticui.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.3.1/semantic.min.js',
    'https://cdn.datatables.net/1.10.19/css/dataTables.semanticui.min.css',
    'https://cdn.rawgit.com/mdehoog/Semantic-UI-Calendar/76959c6f7d33a527b49be76789e984a0a407350b/dist/calendar.min.js',
    'vendor/zxcvbn.js',
    'vendor/moment.min.js',
    filters='jsmin',
    output='scripts/vendor.js')
