from django.conf import settings


def use_mock_data(request):
    return {"USE_MOCK_DATA": getattr(settings, "USE_MOCK_DATA", False)}
