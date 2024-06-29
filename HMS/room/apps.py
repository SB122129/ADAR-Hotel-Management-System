from django.apps import AppConfig


class RoomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'room'



class RoomConfig(AppConfig):
    name = 'room'

    def ready(self):
        import room.signals

class RoomConfig(AppConfig):
    name = 'room'

    def ready(self):
        import room.handlers        
