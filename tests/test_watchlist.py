"""
Tests para endpoints de Watchlist
"""
import pytest
from fastapi import status


class TestCreateWatchlist:
    """Tests para crear items en watchlist"""

    def test_create_watchlist_movie(self, client, auth_headers):
        """Test: Agregar película a watchlist"""
        response = client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tmdb_id"] == 550
        assert data["media_type"] == "movie"
        assert "id" in data

    def test_create_watchlist_tv(self, client, auth_headers):
        """Test: Agregar serie a watchlist"""
        response = client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 1399,
                "media_type": "tv"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["media_type"] == "tv"

    def test_create_watchlist_with_status_plan_to_watch(self, client, auth_headers):
        """Test: Crear watchlist con estado inicial"""
        response = client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "status": "plan_to_watch"
            }
        )
        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["message"] == "Agregado a watchlist exitosamente"
        assert data["watchlist"]['status'] == "plan_to_watch"

    def test_create_watchlist_with_status_watching(self, client, auth_headers):
        """Test: Crear watchlist con estado inicial"""
        response = client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "status": "watching"
            }
        )
        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["message"] == "Agregado a watchlist exitosamente"
        assert data["watchlist"]['status'] == "watching"

    def test_create_watchlist_with_status_completed(self, client, auth_headers):
        """Test: Crear watchlist con estado inicial"""
        response = client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "status": "completed"
            }
        )
        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["message"] == "Agregado a watchlist exitosamente"
        assert data["watchlist"]['status'] == "completed"

    def test_create_watchlist_duplicate(self, client, auth_headers):
        """Test: No permite duplicados en watchlist"""
        # Crear primer item
        client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie"
            }
        )

        # Intentar crear el mismo item
        response = client.post(
            "/api/watchlist",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie"
            }
        )

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_watchlist_unauthenticated(self, client):
        """Test: Sin autenticación no puede agregar a watchlist"""
        response = client.post(
            "/api/watchlist",
            json={
                "tmdb_id": 550,
                "media_type": "movie"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetWatchlist:
    """Tests para listar watchlist"""

    def test_get_watchlist_empty(self, client, auth_headers):
        """Test: Lista vacía cuando no hay items"""
        response = client.get(
            "/api/watchlist",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_watchlist_with_data(self, client, auth_headers, db_session, test_user):
        """Test: Listar watchlist del usuario"""
        from app.models.watchlist import Watchlist, WatchlistStatus

        item1 = Watchlist(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie",
            status=WatchlistStatus.POR_VER
        )
        item2 = Watchlist(
            user_id=test_user.id,
            tmdb_id=1399,
            media_type="tv",
            status=WatchlistStatus.VIENDO
        )
        db_session.add(item1)
        db_session.add(item2)
        db_session.commit()

        response = client.get(
            "/api/watchlist",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        tmdb_ids = [item["tmdb_id"] for item in data]
        assert 550 in tmdb_ids
        assert 1399 in tmdb_ids

    def test_get_watchlist_unauthenticated(self, client):
        """Test: Sin autenticación no puede listar watchlist"""
        response = client.get("/api/watchlist")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateWatchlistStatus:
    """Tests para actualizar estado de watchlist"""

    def test_update_status_success(self, client, auth_headers, db_session, test_user):
        """Test: Actualizar estado de item en watchlist"""
        from app.models.watchlist import Watchlist, WatchlistStatus

        item = Watchlist(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie",
            status=WatchlistStatus.plan_to_watch
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)

        response = client.put(
            f"/api/watchlist/{item.id}",
            headers=auth_headers,
            json={"status": WatchlistStatus.completed}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == WatchlistStatus.completed

    def test_update_status_to_completed(self, client, auth_headers, db_session, test_user):
        """Test: Marcar como vista"""
        from app.models.watchlist import Watchlist, WatchlistStatus

        item = Watchlist(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie",
            status=WatchlistStatus.watching
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)

        response = client.put(
            f"/api/watchlist/{item.id}",
            headers=auth_headers,
            json={"status": WatchlistStatus.completed}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == WatchlistStatus.completed

    def test_update_status_not_found(self, client, auth_headers):
        """Test: Actualizar item inexistente devuelve 404"""
        response = client.put(
            "/api/watchlist/99999",
            headers=auth_headers,
            json={"status": "viendo"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_status_unauthenticated(self, client):
        """Test: Sin autenticación no puede actualizar"""
        response = client.put(
            "/api/watchlist/1",
            json={"status": "viendo"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteWatchlist:
    """Tests para eliminar items de watchlist"""

    def test_delete_watchlist_success(self, client, auth_headers, db_session, test_user):
        """Test: Eliminar item de watchlist exitosamente"""
        from app.models.watchlist import Watchlist

        item = Watchlist(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie"
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)

        response = client.delete(
            f"/api/watchlist/{item.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_watchlist_not_found(self, client, auth_headers):
        """Test: Eliminar item inexistente devuelve 404"""
        response = client.delete(
            "/api/watchlist/99999",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_watchlist_unauthenticated(self, client):
        """Test: Sin autenticación no puede eliminar"""
        response = client.delete("/api/watchlist/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED