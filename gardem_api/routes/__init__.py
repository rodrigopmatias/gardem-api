from fastapi import FastAPI

from gardem_api.routes import auth, farm_note, farms, gardens, probe, seeds


def init_app(app: FastAPI) -> None:
    auth.init_app(app)
    probe.init_app(app)
    seeds.init_app(app)
    gardens.init_app(app)
    farms.init_app(app)
    farm_note.init_app(app)
