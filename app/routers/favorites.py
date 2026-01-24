from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteCheck
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Obtener todos los favoritos del usuario autenticado.
    """
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favorites


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
        favorite_data: FavoriteCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Agregar una película o serie a favoritos.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    """
    # Verificar si ya existe
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.media_type == favorite_data.media_type,
        Favorite.tmdb_id == favorite_data.tmdb_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este contenido ya está en tus favoritos"
        )

    # Crear favorito
    new_favorite = Favorite(
        user_id=current_user.id,
        media_type=favorite_data.media_type,
        tmdb_id=favorite_data.tmdb_id
    )

    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)

    return new_favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
        favorite_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar un favorito por ID.
    """
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == current_user.id
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )

    db.delete(favorite)
    db.commit()

    return None


@router.get("/check/{media_type}/{tmdb_id}", response_model=FavoriteCheck)
async def check_favorite(
        media_type: str,
        tmdb_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Verificar si una película/serie está en favoritos.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.media_type == media_type,
        Favorite.tmdb_id == tmdb_id
    ).first()

    if favorite:
        return FavoriteCheck(is_favorite=True, favorite_id=favorite.id)
    else:
        return FavoriteCheck(is_favorite=False, favorite_id=None)


@router.delete("/{media_type}/{tmdb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite_by_tmdb(
        media_type: str,
        tmdb_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar un favorito por media_type y tmdb_id.
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.media_type == media_type,
        Favorite.tmdb_id == tmdb_id
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )

    db.delete(favorite)
    db.commit()

    return None