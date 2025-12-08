from flask import Flask, redirect, request, render_template, make_response
from urllib.parse import quote
import jwt, os

app = Flask(__name__)

SECRET_KEY = os.getenv('SECRET_KEY')
GH_PAGE_URL = "https://lortega14.github.io/facturacion_insetti/"

@app.route('/validar')
def validate_token():
    token = request.args.get('token')
    
    if not token:
        return make_response(render_template('invalid.html'), 404)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        order_id = payload['order_id']
        item = payload.get('item', '')
        qty = payload.get('qty', 0)
        price = payload.get('price', 0)
        
        print(f"Token válido para orden: {order_id}")
        
        target_url = (
            f"{GH_PAGE_URL}?order_id={order_id}"
            f"&item={quote(str(item))}"
            f"&qty={qty}"
            f"&price={price}"
        )
        
        return redirect(target_url)
    except jwt.ExpiredSignatureError:
        return make_response(render_template('expired.html'), 410)
    except jwt.InvalidTokenError:
        return make_response(render_template('invalid.html'), 404)

@app.route('/')
def index():
    return make_response(render_template('invalid.html'), 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)