# Auth Service

API REST de autenticación construida con FastAPI, PostgreSQL y Redis.

## Tecnologías

- **FastAPI** — framework web async
- **PostgreSQL** — base de datos principal
- **Redis** — blacklist de tokens JWT
- **SQLAlchemy 2.0** — ORM con soporte async
- **Alembic** — migraciones de base de datos
- **bcrypt** — hashing de contraseñas
- **pytest** — tests automatizados

## Arquitectura
app/
├── api/v1/          # Endpoints HTTP (reciben y responden)
├── core/            # Configuración, seguridad y dependencias
├── db/              # Conexiones a PostgreSQL y Redis
├── models/          # Modelos SQLAlchemy (tablas)
├── schemas/         # DTOs Pydantic (validación entrada/salida)
└── services/        # Lógica de negocio

La arquitectura separa responsabilidades en capas — los endpoints no contienen
lógica de negocio, los servicios no saben de HTTP, y los modelos solo representan
la base de datos.

## Decisiones técnicas

**Access token + Refresh token**
El access token tiene vida corta (30 min) para limitar el daño si es robado.
El refresh token permite obtener uno nuevo sin pedir credenciales al usuario.

**Blacklist en Redis**
JWT es stateless por diseño — una vez emitido, es válido hasta que expira.
Redis permite invalidarlo activamente en el logout guardando el token con TTL.

**Mismo mensaje de error en login**
`"Credenciales inválidas"` sin especificar si el email o la contraseña fallaron.
Esto evita que un atacante enumere qué emails están registrados.

**Refresh token de un solo uso**
Al usar un refresh token para obtener uno nuevo, el anterior se revoca
inmediatamente en Redis.

## Endpoints

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | Registrar usuario |
| POST | `/api/v1/auth/login` | No | Iniciar sesión |
| POST | `/api/v1/auth/logout` | Sí | Cerrar sesión |
| POST | `/api/v1/auth/refresh` | No | Renovar tokens |
| GET | `/api/v1/users/me` | Sí | Perfil del usuario |
| GET | `/health` | No | Estado del servicio |

## Correr el proyecto

**Requisitos:** Docker Desktop, Python 3.11+

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/auth-service
cd auth-service

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus valores

# 5. Levantar PostgreSQL y Redis
docker compose up -d

# 6. Aplicar migraciones
alembic upgrade head

# 7. Correr la app
uvicorn app.main:app --reload
```

La documentación interactiva estará disponible en `http://localhost:8000/docs`

## Tests

```bash
pytest tests/ -v
```

## Variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://auth_user:auth_password@localhost:5432/auth_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=tu-secreto-largo-y-aleatorio
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
```