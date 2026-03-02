"""
Tests para endpoints de Reviews
"""
import pytest
from fastapi import status


class TestCreateReview:
    """Tests para crear reviews"""

    def test_create_review_with_rating_and_content(self, client, auth_headers):
        """Test: Crear review completo con rating y contenido"""
        response = client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "rating": 5,
                "review": "Excelente película, muy recomendada"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tmdb_id"] == 550
        assert data["media_type"] == "movie"
        assert data["rating"] == 5
        assert data["review"] == "Excelente película, muy recomendada"
        assert "id" in data

    def test_create_review_only_rating(self, client, auth_headers):
        """Test: Crear review solo con rating (sin contenido)"""
        response = client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 1399,
                "media_type": "tv",
                "rating": 4
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] == 4
        assert data["content"] is None

    def test_create_review_only_content(self, client, auth_headers):
        """Test: Crear review solo con contenido (sin rating)"""
        response = client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 278,
                "media_type": "movie",
                "content": "Gran película sobre esperanza y redención"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] is None
        assert "esperanza" in data["content"]

    def test_create_review_invalid_rating_high(self, client, auth_headers):
        """Test: Rating mayor a 5 rechazado"""
        response = client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "rating": 10
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_review_invalid_rating_low(self, client, auth_headers):
        """Test: Rating menor a 1 rechazado"""
        response = client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "rating": 0
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_review_duplicate(self, client, auth_headers):
        """Test: No permite review duplicado del mismo usuario"""
        # Crear primer review
        client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "rating": 5
            }
        )

        # Intentar crear otro review para el mismo media
        response = client.post(
            "/api/reviews",
            headers=auth_headers,
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "rating": 4
            }
        )

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_review_unauthenticated(self, client):
        """Test: Sin autenticación no puede crear review"""
        response = client.post(
            "/api/reviews",
            json={
                "tmdb_id": 550,
                "media_type": "movie",
                "rating": 5
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_multiple_users_review_same_movie(self, client):
        """Test: Múltiples usuarios pueden reseñar la misma película"""
        movie_id = 550

        # Lista de usuarios existentes en tu BD
        users = [
            {"email": "yergiroska77@gmail.com", "password": "12345678"},
            {"email": "kaniels77@gmail.com", "password": "12345678"},
            {"email": "banguita@example.com", "password": "password123"},
        ]

        reviews_data = [
            (5, "Excelente película, muy recomendada"),
            (3, "No me convenció del todo"),
            (4, "Buena película pero tiene sus fallas"),
        ]

        created_reviews = []

        for user_creds, (rating, review_text) in zip(users, reviews_data):
            # Login para obtener token
            login_response = client.post(
                "/api/login",
                json=user_creds
            )
            assert login_response.status_code == status.HTTP_200_OK
            token = login_response.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Crear review
            response = client.post(
                "/api/reviews",
                headers=headers,
                json={
                    "tmdb_id": movie_id,
                    "media_type": "movie",
                    "rating": rating,
                    "review": review_text
                }
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["rating"] == rating
            assert data["review"] == review_text
            created_reviews.append(data)

        # Verificar que todos tienen IDs diferentes
        ids = [r["id"] for r in created_reviews]
        assert len(ids) == len(set(ids))

        # Verificar que todos son para la misma película
        assert all(r["tmdb_id"] == movie_id for r in created_reviews)

class TestGetReviews:
    """Tests para listar reviews"""

    def test_get_reviews_empty(self, client, auth_headers):
        """Test: Lista vacía cuando no hay reviews"""
        response = client.get(
            "/api/reviews",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_reviews_with_data(self, client, auth_headers, db_session, test_user):
        """Test: Listar reviews del usuario"""
        from app.models.review import Review

        review1 = Review(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie",
            rating=5,
            content="Excelente"
        )
        review2 = Review(
            user_id=test_user.id,
            tmdb_id=1399,
            media_type="tv",
            rating=4
        )
        db_session.add(review1)
        db_session.add(review2)
        db_session.commit()

        response = client.get(
            "/api/reviews",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_reviews_unauthenticated(self, client):
        """Test: Sin autenticación no puede listar reviews"""
        response = client.get("/api/reviews")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateReview:
    """Tests para actualizar reviews"""

    def test_update_review_rating(self, client, auth_headers):
        """Test: Actualizar solo el rating"""
        response = client.put(
            "/api/reviews/7",
            headers=auth_headers,
            json={"rating": 5}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == 5

    def test_update_review_content(self, client, auth_headers):
        """Test: Actualizar solo el contenido"""
        response = client.put(
            "/api/reviews/7",
            headers=auth_headers,
            json={"review": "Obra maestra del cine moderno"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["review"] == "Obra maestra del cine moderno"

    def test_update_review_and_clean_review(self, client, auth_headers):
        """Test: Actualizar rating y contenido"""
        response = client.put(
            "/api/reviews/7",
            headers=auth_headers,
            json={
                "rating": 3,
                "review": ""
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] == 3
        assert data["review"] == ""

    def test_update_review_and_clean_rating(self, client, auth_headers):
        """Test: Actualizar rating y contenido"""
        response = client.put(
            "/api/reviews/7",
            headers=auth_headers,
            json={
                "rating": "",
                "review": "LAGO"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rating"] is None
        assert data["review"] == "LAGO"


    def test_update_review_when_create_new_into_db_rating(self, client, auth_headers, db_session, test_user):
         """
            Test: Actualizar solo el rating
            se crea una nueva reseña para validar la que se crea y se actualiza
         """
         # se crea directamente en la base de datos
         from app.models.review import Review

         review = Review(
             user_id=test_user.id,
             tmdb_id=1368166,
             media_type="movie",
             rating=3
         )
         db_session.add(review)
         db_session.commit()
         db_session.refresh(review)

         # luego se usa el endpoint para cambiar el rating
         response = client.put(
            f"/api/reviews/{review.id}",
             headers=auth_headers,
             json={"rating": 5}
         )
         assert response.status_code == status.HTTP_200_OK
         data = response.json()
         assert data["rating"] == 5 # este nos asegura que el dato fue cambiado

    def test_update_review_when_create_new_into_db_content(self, client, auth_headers, db_session, test_user):
        """Test: Actualizar solo el contenido"""
        from app.models.review import Review

        review = Review(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie",
            content="Buena"
         )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.put(
            f"/api/reviews/{review.id}",
             headers=auth_headers,
            json={"review": "Obra maestra del cine moderno"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["review"] == "Obra maestra del cine moderno"
    #
    # def test_update_review_both(self, client, auth_headers, db_session, test_user):
    #     """Test: Actualizar rating y contenido"""
    #     from app.models.review import Review
    #
    #     review = Review(
    #         user_id=test_user.id,
    #         tmdb_id=550,
    #         media_type="movie",
    #         rating=3,
    #         content="Meh"
    #     )
    #     db_session.add(review)
    #     db_session.commit()
    #     db_session.refresh(review)
    #
    #     response = client.put(
    #         f"/api/reviews/{review.id}",
    #         headers=auth_headers,
    #         json={
    #             "rating": 5,
    #             "content": "Después de una segunda vista, es genial"
    #         }
    #     )
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     data = response.json()
    #     assert data["rating"] == 5
    #     assert "genial" in data["content"]
    #
    # def test_update_review_not_found(self, client, auth_headers):
    #     """Test: Actualizar review inexistente devuelve 404"""
    #     response = client.put(
    #         "/api/reviews/99999",
    #         headers=auth_headers,
    #         json={"rating": 5}
    #     )
    #
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #
    # def test_update_review_unauthenticated(self, client):
    #     """Test: Sin autenticación no puede actualizar"""
    #     response = client.put(
    #         "/api/reviews/1",
    #         json={"rating": 5}
    #     )
    #
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteReview:
    """Tests para eliminar reviews"""

    def test_delete_review_success(self, client, auth_headers, db_session, test_user):
        """Test: Eliminar review exitosamente"""
        from app.models.review import Review

        review = Review(
            user_id=test_user.id,
            tmdb_id=550,
            media_type="movie",
            rating=5
        )
        db_session.add(review)
        db_session.commit()
        db_session.refresh(review)

        response = client.delete(
            f"/api/reviews/{review.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_review_not_found(self, client, auth_headers):
        """Test: Eliminar review inexistente devuelve 404"""
        response = client.delete(
            "/api/reviews/99999",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_review_unauthenticated(self, client):
        """Test: Sin autenticación no puede eliminar"""
        response = client.delete("/api/reviews/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED