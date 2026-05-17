from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate, PasswordUpdate
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)

router = APIRouter()

# OAuth2 scheme para extraer el token del header
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT.
    Se usa en rutas protegidas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    token_data = decode_access_token(token)

    if token_data is None or token_data.email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None:
        raise credentials_exception

    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario.

    - **name**: Nombre completo del usuario
    - **email**: Email único
    - **password**: Contraseña (mínimo 8 caracteres)
    """
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear nuevo usuario
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=get_password_hash(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Crear token de acceso
    token = create_access_token(data={"sub": new_user.email})

    return Token(
        token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Iniciar sesión con email y contraseña.

    - **email**: Email del usuario
    - **password**: Contraseña
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token de acceso
    access_token = create_access_token(data={"sub": user.email})

    return Token(
        token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Cerrar sesión (en JWT es solo del lado del cliente).

    En implementaciones con JWT, el logout se maneja en el frontend
    eliminando el token. Este endpoint es principalmente para mantener
    consistencia con la API de Laravel.
    """
    return {
        "message": "Sesión cerrada exitosamente",
        "user": current_user.email
    }


@router.get("/user", response_model=UserResponse)
async def get_user(current_user: User = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado.
    """
    return UserResponse.model_validate(current_user)


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Obtener perfil del usuario autenticado.
    """
    return UserResponse.model_validate(current_user)


@router.put("/profile")
async def update_profile(
        profile_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Actualizar perfil del usuario.

    - **name**: Nuevo nombre (opcional)
    - **email**: Nuevo email (opcional)
    """
    # Actualizar campos si se proporcionan
    if profile_data.name is not None:
        current_user.name = profile_data.name

    if profile_data.email is not None:
        # Verificar que el nuevo email no esté en uso
        existing_user = db.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )

        current_user.email = profile_data.email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Perfil actualizado exitosamente",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        }
    }


    #return UserResponse.model_validate(current_user)


@router.put("/profile/password")
async def update_password(
        password_data: PasswordUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario.

    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    """
    # Verificar contraseña actual
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    # Actualizar contraseña
    current_user.password = get_password_hash(password_data.new_password)

    db.commit()

    return {
        "message": "Contraseña actualizada exitosamente"
    }


@router.delete("/profile")
async def delete_account(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar cuenta de usuario.
    """
    db.delete(current_user)
    db.commit()

    return {
        "message": "Cuenta eliminada exitosamente"
    }