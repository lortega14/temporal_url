from flask import Flask, redirect, request, render_template, make_response, jsonify
from urllib.parse import quote
import jwt, os, string, random, redis, json

app = Flask(__name__)

SECRET_KEY = os.getenv('SECRET_KEY')
GH_PAGE_URL = "https://lortega14.github.io/facturacion_insetti/"

redis_url = os.getenv('KV_URL') or os.getenv('REDIS_URL')
if not redis_url:
    redis_client = None
    print("ADVERTENCIA: No se detectó KV_URL. La app fallará si intentas guardar datos.")
else:
    redis_client = redis.from_url(redis_url)

@app.route('/api/shorten', methods=['POST'])
def crear_link_corto():
    if not redis_client:
        return jsonify({"error": "BD no configurada"}), 500
    
    auth = request.headers.get("X-Api-Key")
    if auth != SECRET_KEY:
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json

    for _ in range(5):
        chars = string.ascii_letters + string.digits
        short_code = ''.join(random.choice(chars) for _ in range(5))
        if not redis_client.exists(short_code):
            break
        else:
            return jsonify({"error": "No se pudo generar el código"}), 500
    
    try:
        redis_client.set(
            name=short_code,
            value=json.dumps({
                'o': data.get('o'),
                'b': data.get('b'),
                'i': data.get('i'),
                'q': data.get('q'),
                'p': data.get('p')
            }),
            ex=259200 
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"short_url": f"{request.host_url}{short_code}"})

@app.route('/<short_code>')
def redirect_from_short(short_code):
    if not redis_client:
        return "Error de configuración de BD", 500

    raw_data = redis_client.get(short_code)

    if raw_data:
        link_data = json.loads(raw_data)
        target_url = (
            f"{GH_PAGE_URL}?"
            f"order_id={link_data.get('o')}&"
            f"buyer_id={link_data.get('b')}&"
            f"item={quote(str(link_data.get('i') or ''))}&"
            f"qty={link_data.get('q')}&"
            f"price={link_data.get('p')}"
        )
        return redirect(target_url)
    else:
        return make_response(render_template('expired.html'), 404)

@app.route('/')
def index():
    return make_response(render_template('invalid.html'), 404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)