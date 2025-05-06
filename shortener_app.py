
import string
import random
import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# Création base de données SQLite
conn = sqlite3.connect('urls.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS urls (short TEXT PRIMARY KEY, original TEXT)')
conn.commit()

# Générer un ID court
def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# HTML + CSS intégrés
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <title>Raccourcisseur de Liens</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: white;
            padding: 2em;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            text-align: center;
            width: 100%;
            max-width: 500px;
        }
        input[type='url'] {
            padding: 0.6em;
            width: 70%;
            border-radius: 8px;
            border: 1px solid #ccc;
            margin-bottom: 1em;
        }
        button {
            padding: 0.6em 1em;
            border: none;
            border-radius: 8px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .success, .error {
            margin-top: 1em;
            font-weight: bold;
        }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class='container'>
        <h1>🔗 Raccourcisseur de Liens</h1>
        <form method='POST'>
            <input type='url' name='long_url' placeholder='Colle ton URL ici...' required>
            <br>
            <button type='submit'>Raccourcir</button>
        </form>
        {% if short_url %}
            <p class='success'>Lien : <a href='{{ short_url }}' target='_blank'>{{ short_url }}</a></p>
        {% elif error %}
            <p class='error'>{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    error = None
    if request.method == 'POST':
        long_url = request.form.get('long_url')
        if long_url:
            short_id = generate_short_id()
            try:
                c.execute("INSERT INTO urls (short, original) VALUES (?, ?)", (short_id, long_url))
                conn.commit()
                short_url = request.host_url + short_id
            except sqlite3.IntegrityError:
                error = "Erreur lors de la génération du lien."
        else:
            error = "URL invalide."
    return render_template_string(HTML_TEMPLATE, short_url=short_url, error=error)

@app.route('/<short_id>')
def redirect_short(short_id):
    c.execute("SELECT original FROM urls WHERE short=?", (short_id,))
    result = c.fetchone()
    if result:
        return redirect(result[0])
    return render_template_string(HTML_TEMPLATE, short_url=None, error="Lien non trouvé.")

if __name__ == '__main__':
    app.run(debug=True)
