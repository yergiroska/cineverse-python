import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from faker import Faker
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth_service import get_password_hash
from app.database import SessionLocal

# Importar TODOS los modelos para que SQLAlchemy los registre
try:
    from app.models.favorite import Favorite
    from app.models.watchlist import Watchlist
    from app.models.review import Review
    from app.models.search_history import SearchHistory  # ← AÑADIR ESTE
except ImportError as e:
    print(f"⚠️  Advertencia: No se pudieron cargar todos los modelos: {e}")
    pass

fake = Faker('es_ES')

def seed_users(count: int = 20):
    """
    Seed de usuarios para desarrollo y testing

    Args:
        count: Número de usuarios aleatorios a crear (además de los fijos)
    """
    db: Session = SessionLocal()

    try:
        print(f"\n🌱 Iniciando seed de usuarios...\n")

        # Usuarios fijos para desarrollo
        fixed_users = [
            {
                "name": "Yergiroska",
                "email": "yergiroska77@gmail.com",
                "password": "12345678"
            },
            {
                "name": "Kaniels Developer",
                "email": "kaniels77@gmail.com",
                "password": "12345678"
            },
        ]

        created_count = 0
        skipped_count = 0

        # Crear usuarios fijos
        print("📌 Creando usuarios fijos...")
        for user_data in fixed_users:
            if create_user(db, user_data):
                created_count += 1
            else:
                skipped_count += 1

        # Crear usuarios aleatorios con Faker
        print(f"\n🎲 Creando {count} usuarios aleatorios...")
        for i in range(count):
            user_data = {
                "name": fake.name(),
                "email": fake.email(),
                "password": "password123"
            }

            if create_user(db, user_data):
                created_count += 1
            else:
                skipped_count += 1

        db.commit()

        print(f"\n✅ {created_count} usuarios creados")
        print(f"⚠️  {skipped_count} usuarios ya existían")
        print(f"\n🎉 Seed de usuarios completado exitosamente\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error en seeding: {str(e)}\n")
        raise
    finally:
        db.close()


def create_user(db: Session, user_data: dict) -> bool:
    """
    Crea un usuario si no existe

    Returns:
        True si se creó, False si ya existía
    """
    existing_user = db.query(User).filter(
        User.email == user_data["email"]
    ).first()

    if existing_user:
        print(f"   ⏭️  {user_data['email']} (ya existe)")
        return False

    new_user = User(
        name=user_data["name"],
        email=user_data["email"],
        password=get_password_hash(user_data["password"])
    )

    db.add(new_user)
    print(f"   ✅ {user_data['email']}")
    return True


if __name__ == "__main__":
    # Puedes ejecutar directamente este archivo
    seed_users(count=7)