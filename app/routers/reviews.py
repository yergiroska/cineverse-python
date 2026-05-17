from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
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

    return {
        "reviews": [
            {
                "id": review.id,
                "user_id": review.user_id,
                "media_type": review.media_type,
                "tmdb_id": review.tmdb_id,
                "rating": review.rating,
                "review": review.title,
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
    if media_type not in ['movie', 'movies', 'tv']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="media_type debe ser 'movie', 'movies' o 'tv'"
        )

    normalized_type = 'movie' if media_type == 'movies' else media_type

    reviews = db.query(Review).filter(
        Review.media_type == normalized_type,
        Review.tmdb_id == tmdb_id
    ).all()

    return {
        "reviews": [
            {
                "id": review.id,
                "user_id": review.user_id,
                "media_type": review.media_type,
                "tmdb_id": review.tmdb_id,
                "rating": review.rating,
                "review": review.title,        # ← corregido: title no content
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "updated_at": review.updated_at.isoformat() if review.updated_at else None,
                "user": {
                    "id": review.user.id,
                    "name": review.user.name
                }
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
    existing = db.query(Review).filter(
        and_(
            Review.user_id == current_user.id,
            Review.media_type == review_data.media_type,
            Review.tmdb_id == review_data.tmdb_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has creado una review para este contenido"
        )

    new_review = Review(
        user_id=current_user.id,
        media_type=review_data.media_type,
        tmdb_id=review_data.tmdb_id,
        rating=review_data.rating,
        title=review_data.review        # ← corregido: title no content
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
    review = db.query(Review).filter(
        and_(
            Review.id == review_id,
            Review.user_id == current_user.id
        )
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrado"
        )

    update_data = review_data.model_dump(exclude_unset=True)

    if not update_data:
        review.rating = None
        review.title = None             # ← corregido: title no content
    else:
        if "rating" in update_data:
            review.rating = review_data.rating
        if "review" in update_data:
            review.title = review_data.review   # ← corregido: title no content

    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
        review_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    review = db.query(Review).filter(
        and_(
            Review.id == review_id,
            Review.user_id == current_user.id
        )
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    db.delete(review)
    db.commit()

    return None