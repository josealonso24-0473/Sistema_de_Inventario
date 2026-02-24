#!/usr/bin/env python
import os
import sys


def main() -> None:
    """Punto de entrada para la línea de comandos de Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegúrate de que está instalado y "
            "disponible en tu entorno PYTHONPATH, y de haber activado el "
            "entorno virtual adecuado."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

