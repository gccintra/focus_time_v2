# Depois é preciso aprimorar aqui para verificar se as tabelas que estou tentando criar ja existem e não recrialas novamente, implementar migrations
from app import create_app
from app.infra.db import db
from app.infra.entities import *


app = create_app()

with app.app_context():
    db.create_all()
