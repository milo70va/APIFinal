import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()  # Carga las variables de entorno desde el archivo .env

app = Flask(__name__)

# Lee la URI de conexión de MongoDB desde las variables de entorno
MONGO_URI = os.getenv("MONGO_URI")

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb():
    client = MongoClient(MONGO_URI)
    return client

# Configura la conexión de MongoDB al iniciar la aplicación
client = connect_to_mongodb()
ciudadz_db = client.mydatabase  # Reemplaza "mydatabase" con el nombre de tu base de datos

# Ruta para obtener todos los héroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes_collection = ciudadz_db.heroes  # Reemplaza "heroes" con el nombre de tu colección de héroes
    heroes = []
    for hero in heroes_collection.find():
        heroes.append(hero)
    return jsonify({'heroes': heroes})

# Ruta para obtener todos los monstruos
@app.route('/monsters', methods=['GET'])
def get_monsters():
    monsters_collection = ciudadz_db.monsters  # Reemplaza "monsters" con el nombre de tu colección de monstruos
    monsters = []
    for monster in monsters_collection.find():
        monsters.append(monster)
    return jsonify({'monsters': monsters})

# Ruta para obtener un héroe por su ID
@app.route("/heroes/<string:hero_id>", methods=["GET"])
def get_hero(hero_id):
    hero = ciudadz_db.heroes.find_one_or_404({"_id": ObjectId(hero_id)})
    return jsonify({"hero": hero})

# Ruta para obtener un monstruo por su ID
@app.route("/monsters/<string:monster_id>", methods=["GET"])
def get_monster(monster_id):
    monster = ciudadz_db.monsters.find_one_or_404({"_id": ObjectId(monster_id)})
    return jsonify({"monster": monster})

# Ruta para crear un nuevo héroe
@app.route('/heroes', methods=['POST'])
def create_hero():
    data = request.get_json()
    new_hero = {
        "name": data["name"],
        "alias": data["alias"],
        "rank": data["rank"],
        "ability": data["ability"],
        "description": data["description"],
        "battles": data.get("battles", []),
        "fans": data.get("fans", []),
        "sponsors": data.get("sponsors", []),
        "residence": data.get("residence", ""),
        "phone": data.get("phone", ""),
        "monstrific_cells": data.get("mounstrific_cells", {})
    }

    # Agregar las batallas al monstruo enemigo
    for battle in new_hero["battles"]:
        enemy_monster = ciudadz_db.monsters.find_one({"name": battle["monster"]})
        if enemy_monster:
            result_message = f"Victoria {battle.get('result', '')}" if battle["victoria"] == "true" else f"Derrota {battle.get('result', '')}"
            enemy_battle = {
                "hero": data["name"],
                "victoria": battle["victoria"],
                "result": result_message
            }
            enemy_monster_battles = enemy_monster.get("battles", [])
            enemy_monster_battles.append(enemy_battle)
            ciudadz_db.monsters.update_one(
                {"_id": enemy_monster["_id"]},
                {"$set": {"battles": enemy_monster_battles}}
            )

    heroes_collection = ciudadz_db.heroes
    new_hero_id = heroes_collection.insert_one(new_hero).inserted_id
    return jsonify({'message': 'Hero created successfully', 'id': str(new_hero_id)})

# Ruta para crear un nuevo monstruo
@app.route('/monsters', methods=['POST'])
def create_monster():
    data = request.get_json()
    new_monster = {
        "name": data["name"],
        "threat_level": data["threat_level"],
        "battles": data.get("battles", []),
        "monstrific_cells": data.get("mounstrific_cells", {})
    }

    # Agregar las batallas al héroe enemigo
    for battle in new_monster["battles"]:
        enemy_hero = ciudadz_db.heroes.find_one({"name": battle["hero"]})
        if enemy_hero:
            result_message = f"Victoria {battle.get('result', '')}" if battle["victoria"] == "true" else f"Derrota {battle.get('result', '')}"
            enemy_battle = {
                "monster": data["name"],
                "victoria": battle["victoria"],
                "result": result_message
            }
            enemy_hero_battles = enemy_hero.get("battles", [])
            enemy_hero_battles.append(enemy_battle)
            ciudadz_db.heroes.update_one(
                {"_id": enemy_hero["_id"]},
                {"$set": {"battles": enemy_hero_battles}}
            )

    monsters_collection = ciudadz_db.monsters
    new_monster_id = monsters_collection.insert_one(new_monster).inserted_id
    return jsonify({'message': 'Monster created successfully', 'id': str(new_monster_id)})

# Ruta para actualizar un héroe por su ID
@app.route('/heroes/<string:hero_id>', methods=['PUT'])
def update_hero(hero_id):
    data = request.get_json()
    heroes_collection = ciudadz_db.heroes
    result = heroes_collection.update_one({'_id': ObjectId(hero_id)}, {'$set': data})

    # Agregar las batallas actualizadas al monstruo enemigo
    for battle in data.get("battles", []):
        enemy_monster = ciudadz_db.monsters.find_one({"name": battle["monster"]})
        if enemy_monster:
            result_message = f"Victoria {battle.get('result', '')}" if battle["victoria"] == "true" else f"Derrota {battle.get('result', '')}"
            enemy_battle = {
                "hero": data["name"],
                "victoria": battle["victoria"],
                "result": result_message
            }
            enemy_monster_battles = enemy_monster.get("battles", [])
            enemy_monster_battles.append(enemy_battle)
            ciudadz_db.monsters.update_one(
                {"_id": enemy_monster["_id"]},
                {"$set": {"battles": enemy_monster_battles}}
            )

    if result.modified_count > 0:
        return jsonify({'message': 'Hero updated successfully'})
    else:
        return jsonify({'message': 'Hero not found or not updated'})

# Ruta para actualizar un monstruo por su ID
@app.route('/monsters/<string:monster_id>', methods=['PUT'])
def update_monster(monster_id):
    data = request.get_json()
    monsters_collection = ciudadz_db.monsters
    result = monsters_collection.update_one({'_id': ObjectId(monster_id)}, {'$set': data})

    # Agregar las batallas actualizadas al héroe enemigo
    for battle in data.get("battles", []):
        enemy_hero = ciudadz_db.heroes.find_one({"name": battle["hero"]})
        if enemy_hero:
            result_message = f"Victoria {battle.get('result', '')}" if battle["victoria"] == "true" else f"Derrota {battle.get('result', '')}"
            enemy_battle = {
                "monster": data["name"],
                "victoria": battle["victoria"],
                "result": result_message
            }
            enemy_hero_battles = enemy_hero.get("battles", [])
            enemy_hero_battles.append(enemy_battle)
            ciudadz_db.heroes.update_one(
                {"_id": enemy_hero["_id"]},
                {"$set": {"battles": enemy_hero_battles}}
            )

    if result.modified_count > 0:
        return jsonify({'message': 'Monster updated successfully'})
    else:
        return jsonify({'message': 'Monster not found or not updated'})

# Ruta para obtener héroes expuestos a células monstríficas
@app.route('/heroes/exposed', methods=['GET'])
def get_exposed_heroes():
    heroes_collection = ciudadz_db.heroes
    exposed_heroes = heroes_collection.find({"monstrific_cells.exposed": True})
    exposed_heroes_list = [hero for hero in exposed_heroes]
    return jsonify({'exposed_heroes': exposed_heroes_list})

# Ruta para obtener héroes no expuestos a células monstríficas
@app.route('/heroes/not_exposed', methods=['GET'])
def get_not_exposed_heroes():
    heroes_collection = ciudadz_db.heroes
    not_exposed_heroes = heroes_collection.find({"monstrific_cells.exposed": False})
    not_exposed_heroes_list = [hero for hero in not_exposed_heroes]
    return jsonify({'not_exposed_heroes': not_exposed_heroes_list})

# Ruta para obtener monstruos expuestos a células monstríficas
@app.route('/monsters/exposed', methods=['GET'])
def get_exposed_monsters():
    monsters_collection = ciudadz_db.monsters
    exposed_monsters = monsters_collection.find({"monstrific_cells.exposed": True})
    exposed_monsters_list = [monster for monster in exposed_monsters]
    return jsonify({'exposed_monsters': exposed_monsters_list})

# Ruta para obtener monstruos no expuestos a células monstríficas
@app.route('/monsters/not_exposed', methods=['GET'])
def get_not_exposed_monsters():
    monsters_collection = ciudadz_db.monsters
    not_exposed_monsters = monsters_collection.find({"monstrific_cells.exposed": False})
    not_exposed_monsters_list = [monster for monster in not_exposed_monsters]
    return jsonify({'not_exposed_monsters': not_exposed_monsters_list})

# Ruta para obtener los 10 héroes más fuertes (basados en batallas ganadas)
@app.route('/heroes/top10', methods=['GET'])
def get_top_10_heroes():
    heroes_collection = ciudadz_db.heroes
    top_10_heroes = heroes_collection.find({"battles.victoria": "true"}).sort([("battles.victoria", -1)]).limit(10)
    top_10_heroes_list = [hero for hero in top_10_heroes]
    return jsonify({'top_10_heroes': top_10_heroes_list})

if __name__ == '__main__':
    app.run()