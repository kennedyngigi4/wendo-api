from django.apps import AppConfig


class ProfessionalsConfig(AppConfig):
    name = 'apps.professionals'


    def ready(self):
        import apps.professionals.signals



