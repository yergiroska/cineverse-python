# CineVerse API

> API REST backend para CineVerse — plataforma de seguimiento de películas y series. Construida con **FastAPI** y **PostgreSQL**.

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Variables de Entorno](#variables-de-entorno)
- [Migraciones](#migraciones)
- [Endpoints](#endpoints)
- [Autenticación](#autenticación)
- [Funcionalidades](#funcionalidades)

---

## Descripción

CineVerse API provee toda la lógica backend para una aplicación full-stack de seguimiento de películas y series. Se integra con la **TMDB API** para obtener datos en tiempo real, y gestiona autenticación de usuarios, favoritos, listas de seguimiento, reseñas e historial de búsqueda.

El frontend (React + Vite) está disponible en: [movies-series-frontend](https://github.com/yergiroska/movies-series-frontend).

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| FastAPI | 0.128.0 | Framework web |
| Python | 3.11+ | Runtime |
| PostgreSQL | 16+ | Base de datos principal |
| SQLAlchemy | 2.0 | ORM |
| Alembic | 1.18 | Migraciones de base de datos |
| Pydantic | 2.12 | Validación de datos |
| python-jose | 3.5 | Autenticación JWT |
| passlib + bcrypt | 1.7 / 4.0 | Hash de contraseñas |
| Redis | 7.1 | Caché (cliente sync para listas de usuario + cliente async para TMDB) |
| httpx | 0.28 | Cliente HTTP para TMDB |
| uvicorn | 0.40 | Servidor ASGI |
| pytest | 9.0 | Testing |
| TMDB API | v3 | Fuente de datos de películas y series |

---

## Estructura del Proyecto

```
cineverse-python/
├── app/
│   ├── core/
│   │   └── redis.py              # Cliente Redis síncrono (favoritos, watchlist)
│   ├── models/
│   │   ├── user.py
│   │   ├── favorite.py
│   │   ├── watchlist.py
│   │   ├── review.py
│   │   └── search_history.py
│   ├── routers/
│   │   ├── auth.py               # Registro, login, perfil + dependency get_current_user
│   │   ├── movies.py             # Integración TMDB películas
│   │   ├── tv.py                 # Integración TMDB series
│   │   ├── favorites.py
│   │   ├── watchlist.py
│   │   ├── reviews.py
│   │   └── search_history.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── favorite.py
│   │   ├── watchlist.py
│   │   ├── review.py
│   │   └── search_history.py
│   ├── services/
│   │   ├── auth_service.py       # JWT + hash de contraseñas
│   │   ├── tmdb_service.py       # Cliente TMDB API con caché async
│   │   └── cache_service.py      # Caché Redis asíncrono para TMDB
│   ├── config.py                 # Configuración (pydantic-settings)
│   ├── database.py               # Engine + sesión SQLAlchemy
│   └── main.py                   # Entry point + CORS + startup/shutdown Redis
├── alembic/
│   ├── versions/                 # Archivos de migración
│   └── env.py
├── tests/
│   ├── conftest.py               # Fixtures compartidos
│   ├── test_auth.py
│   ├── test_favorites.py
│   ├── test_watchlist.py
│   ├── test_reviews.py
│   ├── test_movies.py
│   ├── test_tv.py
│   └── test_search_history.py
├── seeders/
│   ├── run_seeders.py
│   └── user_seeder.py
├── docs/
│   └── resumen-proyecto.md       # Análisis técnico detallado del proyecto
├── requirements.txt
├── alembic.ini
└── .env
```

---

## Instalación

### Requisitos previos

- Python 3.11+
- PostgreSQL 16+
- Redis (opcional, para caché)
- API key de TMDB → [themoviedb.org](https://www.themoviedb.org/settings/api)

### Pasos

**1. Clonar el repositorio**

```bash
git clone https://github.com/yergiroska/cineverse-python.git
cd cineverse-python
```

**2. Crear y activar entorno virtual**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus valores
```

**5. Ejecutar migraciones**

```bash
alembic upgrade head
```

**6. Iniciar el servidor**

```bash
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en `http://localhost:8000`  
Documentación interactiva (Swagger UI) en `http://localhost:8000/api/docs`  
Documentación alternativa (ReDoc) en `http://localhost:8000/api/redoc`

---

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/cineverse

# JWT
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# TMDB
TMDB_API_KEY=tu-api-key-de-tmdb
TMDB_BASE_URL=https://api.themoviedb.org/3

# CORS
CORS_ORIGINS=http://localhost:5173

# Entorno
ENVIRONMENT=development
```

> Redis se conecta a `localhost:6379` por defecto. No requiere variable de entorno adicional.

---

## Migraciones

El proyecto usa **Alembic** para gestionar migraciones de base de datos.

```bash
# Aplicar todas las migraciones
alembic upgrade head

# Crear una nueva migración
alembic revision --autogenerate -m "descripción"

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history
```

### Esquema de Base de Datos

| Tabla | Descripción |
|---|---|
| `users` | Cuentas de usuario y credenciales |
| `favorites` | Películas y series favoritas por usuario |
| `watchlists` | Lista de seguimiento con estado (`plan_to_watch` / `watching` / `completed`) |
| `reviews` | Reseñas con puntuación 1-5 estrellas y texto |
| `search_histories` | Historial de búsquedas por usuario |

> El contenido (películas/series) no se almacena localmente. Cada registro usa `media_type` (`movie` o `tv`) + `tmdb_id` para identificar el título, y los datos se obtienen de TMDB en tiempo real.

---

## Endpoints

### Autenticación

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| POST | `/api/register` | No | Registrar nuevo usuario → devuelve token + usuario |
| POST | `/api/login` | No | Iniciar sesión → devuelve token + usuario |
| POST | `/api/logout` | Sí | Cerrar sesión (JWT sin blacklist, acción del lado del cliente) |
| GET | `/api/user` | Sí | Obtener usuario actual |
| GET | `/api/profile` | Sí | Obtener perfil del usuario |
| PUT | `/api/profile` | Sí | Actualizar nombre y/o email |
| PUT | `/api/profile/password` | Sí | Cambiar contraseña |
| DELETE | `/api/profile` | Sí | Eliminar cuenta |

### Películas

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/movies/popular` | No | Películas populares |
| GET | `/api/movies/top-rated` | No | Películas mejor valoradas |
| GET | `/api/movies/upcoming` | No | Próximos estrenos |
| GET | `/api/movies/search?query=` | No | Buscar películas |
| GET | `/api/movies/genres/list` | No | Lista de géneros |
| GET | `/api/movies/discover` | No | Descubrir por género u ordenamiento |
| GET | `/api/movies/{id}` | No | Detalle de película |
| GET | `/api/movies/{id}/similar` | No | Películas similares |
| GET | `/api/movies/{id}/providers` | No | Plataformas de streaming |

### Series

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/tv/popular` | No | Series populares |
| GET | `/api/tv/top-rated` | No | Series mejor valoradas |
| GET | `/api/tv/on-the-air` | No | Series en emisión |
| GET | `/api/tv/search?query=` | No | Buscar series |
| GET | `/api/tv/genres/list` | No | Lista de géneros |
| GET | `/api/tv/discover` | No | Descubrir por género u ordenamiento |
| GET | `/api/tv/{id}` | No | Detalle de serie |
| GET | `/api/tv/{id}/similar` | No | Series similares |
| GET | `/api/tv/{id}/providers` | No | Plataformas de streaming |

### Favoritos

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/favorites/` | Sí | Obtener favoritos del usuario (filtro `media_type`, paginación) |
| POST | `/api/favorites/` | Sí | Agregar a favoritos |
| DELETE | `/api/favorites/{id}` | Sí | Eliminar de favoritos por ID |
| DELETE | `/api/favorites/{media_type}/{tmdb_id}` | Sí | Eliminar de favoritos por tipo y ID de TMDB |
| GET | `/api/favorites/check/{media_type}/{tmdb_id}` | Sí | Verificar si un título está en favoritos |

### Watchlist

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/watchlist/` | Sí | Obtener lista (filtros `media_type`, `status`, paginación) |
| POST | `/api/watchlist/` | Sí | Agregar a la lista |
| PUT | `/api/watchlist/{id}` | Sí | Actualizar estado |
| DELETE | `/api/watchlist/{id}` | Sí | Eliminar de la lista |
| GET | `/api/watchlist/check/{media_type}/{tmdb_id}` | Sí | Verificar si un título está en watchlist y su estado |

**Estados válidos de watchlist:** `plan_to_watch` · `watching` · `completed`

### Reseñas

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/reviews/` | Sí | Obtener reseñas del usuario |
| POST | `/api/reviews/` | Sí | Crear reseña |
| PUT | `/api/reviews/{id}` | Sí | Actualizar reseña |
| DELETE | `/api/reviews/{id}` | Sí | Eliminar reseña |
| GET | `/api/reviews/{media_type}/{tmdb_id}` | No | Ver todas las reseñas de un título |

### Historial de Búsqueda

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/search/history/` | Sí | Obtener historial (máx. 50 entradas) |
| POST | `/api/search/history/` | Sí | Guardar una búsqueda |
| DELETE | `/api/search/history/` | Sí | Limpiar todo el historial |
| DELETE | `/api/search/history/{id}` | Sí | Eliminar una entrada específica |

---

## Autenticación

La API usa **JWT Bearer tokens**. Incluye el token en el header `Authorization` para los endpoints protegidos:

```
Authorization: Bearer <tu_token>
```

Los tokens se devuelven al registrarse o iniciar sesión. El logout no invalida el token en el servidor — la expiración y la eliminación del token son responsabilidad del cliente.

---

## Funcionalidades

- **Autenticación JWT** — tokens seguros con hash de contraseñas bcrypt
- **Integración TMDB** — datos en tiempo real de películas y series, géneros, proveedores y títulos similares (idioma `es-ES` por defecto)
- **Favoritos** — agregar/quitar con verificación de duplicados
- **Watchlist** — seguimiento con estados: `plan_to_watch`, `watching`, `completed`
- **Reseñas** — puntuación 1-5 estrellas + texto, una por usuario por título
- **Historial de búsqueda** — registro de búsquedas del usuario, con límite de 50 entradas
- **Caché con Redis** — dos capas: caché async para respuestas TMDB (TTL por tipo), caché sync para listas de usuario (invalidación automática)
- **Migraciones con Alembic** — esquema de base de datos versionado
- **Swagger UI** — documentación interactiva auto-generada en `/api/docs`
- **CORS configurado** — listo para conectar con el frontend React

---

*Desarrollado por [Yergiroska](https://github.com/yergiroska) — Barcelona, España*
