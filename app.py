from flask import Flask, render_template, request, redirect, url_for, Response
from functools import wraps
import pandas as pd
import os

app = Flask(__name__)

USUARIO = 'admin'
CLAVE = 'clave123'

def requerir_autenticacion(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USUARIO or auth.password != CLAVE:
            return Response(
                'Acceso restringido.\nNecesitás usuario y contraseña.', 401,
                {'WWW-Authenticate': 'Basic realm="Acceso restringido"'}
            )
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    nombre = request.form['nombre']
    participacion = request.form['participacion']
    estudios_biblicos = request.form['estudios_biblicos']
    cantidad_estudios = request.form.get('cantidad_estudios', '')
    es_precursor = request.form.get('es_precursor', 'No')
    horas_precursor = request.form.get('horas_precursor', '')

    respuesta = {
        'Nombre': nombre,
        'Participación': participacion,
        'Estudios Bíblicos': estudios_biblicos,
        'Cantidad Estudios': cantidad_estudios,
        '¿Precursor?': es_precursor,
        'Horas Precursor': horas_precursor
    }

    df = pd.DataFrame([respuesta])
    archivo = "respuestas.xlsx"
    if os.path.exists(archivo):
        existente = pd.read_excel(archivo)
        df = pd.concat([existente, df], ignore_index=True)
    df.to_excel(archivo, index=False)

    return render_template('gracias.html', nombre=nombre)

@app.route('/respuestas')
@requerir_autenticacion
def respuestas():
    archivo = "respuestas.xlsx"
    if os.path.exists(archivo):
        df = pd.read_excel(archivo)
        return render_template('respuestas.html', tablas=[df.to_html(classes='data', header="true", index=False)])
    else:
        return "No hay respuestas registradas aún."

if __name__ == '__main__':
    app.run()
