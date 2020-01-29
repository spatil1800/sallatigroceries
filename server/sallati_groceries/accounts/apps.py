from django.apps import AppConfig


class AccountsAppConfig(AppConfig):
    name = "accounts"

    def ready(self):
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
