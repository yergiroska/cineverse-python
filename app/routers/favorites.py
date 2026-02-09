from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteCheck
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_favorites(
        media_type: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)

    if media_type:
        query = query.filter(Favorite.media_type == media_type)

    # Obtener total antes de paginar
    total = query.count()

    # Aplicar paginación
    favorites = query.order_by(Favorite.created_at.desc()).limit(limit).offset(offset).all()

    # Formatear como Laravel
    return {
        "favorites": [
            {
                "id": fav.id,
                "user_id": fav.user_id,
                "tmdb_id": fav.tmdb_id,
                "media_type": fav.media_type,
                "created_at": fav.created_at.isoformat() if fav.created_at else None,
                "updated_at": fav.updated_at.isoformat() if fav.updated_at else None,
            }
            for fav in favorites
        ],
        "total": total
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
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

    # Formatear como Laravel
    return {
        "message": "Agregado a favoritos exitosamente",
        "favorite": {
            "id": new_favorite.id,
            "user_id": new_favorite.user_id,
            "tmdb_id": new_favorite.tmdb_id,
            "media_type": new_favorite.media_type,
            "created_at": new_favorite.created_at.isoformat() if new_favorite.created_at else None,
            "updated_at": new_favorite.updated_at.isoformat() if new_favorite.updated_at else None,
        }
    }


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