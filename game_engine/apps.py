from django.apps import AppConfig


class GameEngineConfig(AppConfig):
    name = 'game_engine'

    def ready(self):
        import game_engine.signals
