import sys
from pathlib import Path

# Añadir el directorio raíz al path para importaciones
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from seeders.user_seeder import seed_users


def run_all_seeders():
    """Ejecuta todos los seeders en orden"""
    print("\n" + "=" * 50)
    print("🌱 EJECUTANDO SEEDERS DE CINEVERSE")
    print("=" * 50)

    # Ejecutar seeders
    seed_users(count=20)

    # Aquí puedes añadir más seeders cuando los crees:
    # seed_movies()
    # seed_watchlists()
    # seed_reviews()

    print("=" * 50)
    print("✨ TODOS LOS SEEDERS COMPLETADOS")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all_seeders()