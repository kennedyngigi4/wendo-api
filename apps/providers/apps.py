from django.apps import AppConfig


class ProvidersConfig(AppConfig):
    name = 'apps.providers'




    def ready(self):
        import apps.providers.signals



