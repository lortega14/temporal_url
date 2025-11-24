from flask import Flask, redirect, request, render_template, make_response
import jwt, os

app = Flask(__name__)

SECRET_KEY = os.getenv('SECRET_KEY')
GH_PAGE_URL = "https://lortega14.github.io/facturacion_insetti/"

@app.route('/validar')
def validate_token():
    token = request.args.get('token') # Obtenemos el token de la URL
    
    if not token:
        return make_response(render_template('invalid.html'), 404)

    try:
        # Validamos firma y expiración (JWT lo hace automático con 'exp')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        order_id = payload['order_id']
        
        print(f"Token válido para orden: {order_id}")
        
        # Redirige al Formulario Estático pasándole el order_id
        # El usuario final verá: facturacion.insetti.com.mx/?order_id=12345
        return redirect(f"{GH_PAGE_URL}?order_id={order_id}")
        
    except jwt.ExpiredSignatureError:
        return make_response(render_template('expired.html'), 410)
    except jwt.InvalidTokenError:
        return make_response(render_template('invalid.html'), 404)

@app.route('/')
def index():
    return "Portal de validación de facturas Insetti."

if __name__ == '__main__':
    app.run(debug=True, port=5000)