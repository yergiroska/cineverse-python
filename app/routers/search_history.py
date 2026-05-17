from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.search_history import SearchHistory
from app.schemas.search_history import SearchHistoryCreate, SearchHistoryResponse
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[SearchHistoryResponse])
async def get_search_history(
        limit: int = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Obtener el historial de búsquedas del usuario autenticado.

    - **limit**: Número máximo de resultados (default: 20, max: 50)
    """
    if limit > 50:
        limit = 50

    searches = db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).order_by(desc(SearchHistory.created_at)).limit(limit).all()

    return searches


@router.post("/", response_model=SearchHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_search_history(
        search_data: SearchHistoryCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Guardar una búsqueda en el historial.

    - **query**: Texto de búsqueda
    """
    # Crear entrada de historial
    new_search = SearchHistory(
        user_id=current_user.id,
        query=search_data.query.strip()
    )

    db.add(new_search)
    db.commit()
    db.refresh(new_search)

    return new_search


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_search_history(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Limpiar todo el historial de búsquedas del usuario.
    """
    db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.id
    ).delete()

    db.commit()

    return None


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_history(
        search_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Eliminar una entrada específica del historial por ID.
    """
    search = db.query(SearchHistory).filter(
        SearchHistory.id == search_id,
        SearchHistory.user_id == current_user.id
    ).first()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada de historial no encontrada"
        )

    db.delete(search)
    db.commit()

    return None