from fastapi import FastAPI

from gardem_api.routes import auth, farms, gardens, notes, probe, seeds


def init_app(app: FastAPI) -> None:
    auth.init_app(app)
    probe.init_app(app)
    seeds.init_app(app)
    gardens.init_app(app)
    farms.init_app(app)
    notes.init_app(app)
