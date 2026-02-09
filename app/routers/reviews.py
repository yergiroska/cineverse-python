from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewWithUser
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_reviews(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(Review.user_id == current_user.id).all()

    # Formatear como Laravel
    return {
        "reviews": [
            {
                "id": review.id,
                "user_id": review.user_id,
                "media_type": review.media_type,
                "tmdb_id": review.tmdb_id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "updated_at": review.updated_at.isoformat() if review.updated_at else None,
            }
            for review in reviews
        ]
    }


@router.get("/{media_type}/{tmdb_id}")
async def get_reviews_by_media(
        media_type: str,
        tmdb_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todas las reviews de una película/serie específica (de todos los usuarios).
    Compatible con formato Laravel.
    """
    # Validar media_type
    if media_type not in ['movie', 'movies', 'tv']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="media_type debe ser 'movie', 'movies' o 'tv'"
        )

    # Normalizar media_type (movies -> movie)
    normalized_type = 'movie' if media_type == 'movies' else media_type

    # Buscar reviews
    reviews = db.query(Review).filter(
            Review.media_type == normalized_type,
            Review.tmdb_id == tmdb_id

    ).all()

    # Formatear como Laravel
    return {
        "reviews": [
            {
                "id": review.id,
                "user_id": review.user_id,
                "media_type": review.media_type,
                "tmdb_id": review.tmdb_id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "updated_at": review.updated_at.isoformat() if review.updated_at else None,
            }
            for review in reviews
        ],
        "total": len(reviews)
    }

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
        review_data: ReviewCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Crear una review para una película o serie.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB
    - **rating**: Calificación 1-5 (opcional)
    - **content**: Texto de la reseña (opcional)

    Nota: Debes proporcionar al menos rating o content.
    """
    # Verificar si ya existe una review para este media
    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.media_type == review_data.media_type,
        Review.tmdb_id == review_data.tmdb_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has creado una review para este contenido"
        )

    # Crear review
    new_review = Review(
        user_id=current_user.id,
        media_type=review_data.media_type,
        tmdb_id=review_data.tmdb_id,
        rating=review_data.rating,
        content=review_data.content
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
        review_id: int,
        review_data: ReviewUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Actualizar una review existente.

    - **rating**: Nueva calificación (opcional)
    - **content**: Nuevo contenido (opcional)
    """
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    # Actualizar campos si se proporcionan
    if review_data.rating is not None:
        review.rating = review_data.rating

    if review_data.content is not None:
        review.content = review_data.content

    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
        review_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar una review por ID.
    """
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    db.delete(review)
    db.commit()

    return None


@router.get("/{media_type}/{tmdb_id}", response_model=List[ReviewWithUser])
async def get_reviews_by_media(
        media_type: str,
        tmdb_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener todas las reviews de una película/serie específica.

    - **media_type**: 'movie' o 'tv'
    - **tmdb_id**: ID de TMDB

    Este endpoint es público (no requiere autenticación).
    """
    reviews = db.query(Review, User.name).join(
        User, Review.user_id == User.id
    ).filter(
        Review.media_type == media_type,
        Review.tmdb_id == tmdb_id
    ).all()

    # Construir respuesta con nombre de usuario
    result = []
    for review, user_name in reviews:
        review_dict = {
            "id": review.id,
            "user_id": review.user_id,
            "media_type": review.media_type,
            "tmdb_id": review.tmdb_id,
            "rating": review.rating,
            "content": review.content,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "user_name": user_name
        }
        result.append(ReviewWithUser(**review_dict))

    return result