# app.py (fragmentos)
from flask import Flask, redirect, url_for, make_response, render_template, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

app = Flask(__name__, static_folder='static', template_folder='templates')

# Desactiva caché de estáticos en desarrollo para ver CSS al recargar
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

SECRET_KEY = '...'
GH_PAGE_URL = "https://lortega14.github.io/facturacion_insetti/"
EXPIRATION_IN_SECONDS = 72 * 60 * 60
s = URLSafeTimedSerializer(SECRET_KEY)

@app.after_request
def add_header(resp):
    # Evita cacheo agresivo en dev: recargas muestran CSS nuevo
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.route('/')
def index():
    data_to_protect = {'user_id': 123, 'form_id': 'A'}
    token = s.dumps(data_to_protect, salt='form-access')
    temp_link = url_for('validate_link', token=token, _external=True)
    return render_template('index.html', temp_link=temp_link)

@app.route('/validar/<token>')
def validate_link(token):
    try:
        data = s.loads(token, salt='form-access', max_age=EXPIRATION_IN_SECONDS)
        print(f"Token válido. Redirigiendo. Datos: {data}")
        return redirect(GH_PAGE_URL)
    except SignatureExpired:
        print("Intento con token expirado.")
        return make_response(render_template('expired.html'), 410)
    except (BadTimeSignature, Exception):
        print("Intento con token inválido.")
        return make_response(render_template('invalid.html'), 404)

@app.errorhandler(404)
def page_not_found(e):
    print(f"Ruta no encontrada: {e}")
    return make_response(render_template('invalid.html'), 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
