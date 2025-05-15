#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(rules=('-missions', '-planets',)) for scientist in Scientist.query.all()]

        result = make_response(
            scientists,
            200
        )

        return result

    def post(self):

        fields = request.get_json()

        try:
            new_scientist = Scientist(
                name=fields['name'],
                field_of_study=fields['field_of_study']
            )

            db.session.add(new_scientist)
            db.session.commit()

            result = make_response(
                new_scientist.to_dict(),
                201
            )

            return result

        except ValueError:
            result = make_response(
                {"errors": ["validation errors"]},
                400
            )

            return result

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first().to_dict()

        result = make_response(
            scientist,
            200
        )

        return result

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()

        if not scientist:
            result = make_response(
                { "error": "Scientist not found" },
                404
            )

            return result

        fields = request.get_json()

        try:
            for field in fields:
                setattr(scientist, field, fields[field])
            db.session.add(scientist)
            db.session.commit()

            result = make_response(
                scientist.to_dict(rules=('-planets', '-missions')),
                202
            )

            return result

        except ValueError:
            result = make_response(
                {"errors": ["validation errors"]},
                400
            )

            return result

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()

        if not scientist:
            result = make_response(
                { "error": "Scientist not found" },
                404
            )

            return result

        db.session.delete(scientist)
        db.session.commit()

        result = make_response(
            {},
            204
        )

        return result

api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=('-scientists', '-missions')) for planet in Planet.query.all()]

        result = make_response(
            planets,
            200
        )

        return result

api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        fields = request.get_json()

        try:
            new_mission = Mission(
                name=fields['name'],
                scientist_id=fields['scientist_id'],
                planet_id=fields['planet_id']
            )

            db.session.add(new_mission)
            db.session.commit()

            result = make_response(
                new_mission.to_dict(),
                201
            )

            return result

        except ValueError:
            result = make_response(
                {"errors": ["validation errors"]},
                400
            )

            return result

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
