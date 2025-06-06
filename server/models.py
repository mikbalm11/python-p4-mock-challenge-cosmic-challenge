from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    missions = db.relationship('Mission', backref='planet', cascade='all, delete-orphan')

    serialize_rules = ('-missions.planet', '-scientists.planets')

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    missions = db.relationship('Mission', backref='scientist', cascade='all, delete-orphan')

    serialize_rules = ('-missions.scientist', '-planets.scientists')

    @validates('name')
    def validates_name(self, key, name):
        if not name:
            raise ValueError('Scientists must have a name.')
        return name
    
    @validates('field_of_study')
    def validates_field_of_study(self, key, field_of_study):
        if not field_of_study:
            raise ValueError('Scientists must have a field of study.')
        return field_of_study

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    serialize_rules = ('-scientist.missions', '-planet.missions')

    @validates('name')
    def validates_name(self, key, name):
        if not name:
            raise ValueError('Missions must have a name.')
        return name

    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if not scientist_id:
            raise ValueError('Missions must have scientist ID.')
        return scientist_id
        
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if not planet_id:
            raise ValueError('Missions must have planet ID.')
        return planet_id
