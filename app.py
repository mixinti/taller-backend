from flask import Flask, request, render_template, redirect
import requests
import os

from models import db
from models import Favorite

# instancia de flask 
app = Flask(__name__)

# configuraciones de base de datos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# url de la api
API_URL = 'https://rickandmortyapi.com/api/character'

@app.route("/")
def index():
    # request que envia el usuario desde el html
    page = request.args.get('page', 1)
    # obtenemos el parametro name de la url y guardamos en name
    name =request.args.get('name')

    if name:
        # hago la peticion get a la api
        response = requests.get(API_URL, params={'name': name})

        if response.status_code != 200:
            return render_template('index.html', characters=[], search=True, error_message='Personaje no encontrado')
        
        data = response.json()
        return render_template('index.html', characters=data['results'], search=True)

    # requests a la api
    response = requests.get(API_URL, params={'page': page})
    
    data = response.json()

    return render_template('index.html', characters=data['results'], info=data['info'], page=int(page), search=False)


# ruta para guardar los personajes
@app.route('/save', methods=['POST'])
def save():
    api_id = request.form['api_id']
    name = request.form['name']
    image = request.form['image']
    page = request.form.get('page', 1)

    # esto nos permite guardar en la base de datos solamente si el dato todavia no existe
    if not Favorite.query.filter_by(api_id=api_id).first():
        fav = Favorite(api_id=api_id, name=name, image=image)

        db.session.add(fav)
        db.session.commit()

    return redirect(f'/?page={page}')

@app.route("/favorites")
def favorites():
    favorites = Favorite.query.all()
    return render_template("favorites.html", favorites=favorites)


# ruta eliminar personajes
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    fav = Favorite.query.get(id)
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect("/favorites")