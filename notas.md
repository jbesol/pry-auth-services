# Notas personales — Auth Service

## ¿Para qué sirve en la realidad?

Cualquier aplicación que tenga usuarios necesita autenticación. Este servicio
resuelve exactamente eso — quién eres y si tienes permiso de estar aquí.

**E-commerce** — cuando el usuario hace login en una tienda online, este servicio
emite los tokens. Cada vez que agrega algo al carrito o hace un pago, el access
token viaja en el header y el servicio valida que es quien dice ser.

**App de delivery** — el rider hace login en la app móvil, recibe sus tokens.
Cada request que hace — aceptar pedido, marcar entrega — pasa por este servicio primero.

**SaaS empresarial** — una empresa con múltiples productos internos (CRM, inventario,
nómina) puede usar un solo Auth Service centralizado. Todos los productos confían
en los tokens que este servicio emite.

---

## ¿Por qué reusar este mismo servicio?

En arquitecturas modernas se usan microservicios — servicios pequeños con
responsabilidades específicas:

```
Auth Service     →  solo maneja identidad y tokens
Product Service  →  solo maneja productos
Order Service    →  solo maneja pedidos
Payment Service  →  solo maneja pagos
```

Los otros servicios simplemente le preguntan al Auth Service si un token es válido.
Si la respuesta es sí, continúan con su trabajo. El Auth Service no sabe nada de
productos ni pedidos — solo sabe si un token es válido y a quién pertenece.

---

## ¿Cómo usarlo en otro proyecto mío?

En lugar de construir auth desde cero en cada proyecto, arranco este servicio
y mi nueva API lo consume directamente:

```python
# En cualquier otro proyecto FastAPI
import httpx

async def get_current_user(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401)
        return response.json()
```

El otro proyecto no sabe nada de JWT ni bcrypt — solo le pregunta al Auth Service
y confía en su respuesta.

---

## ¿Cómo usarlo en producción real?

1. Auth Service deployado en su propio servidor/contenedor
2. Cada microservicio conoce la URL del Auth Service
3. Cada request protegido pasa por validación antes de procesarse

Para esto se necesita Docker + deployment (Proyecto 4).

La forma más efectiva de mostrarlo en el portafolio es tenerlo deployado
con una URL pública y enlazarlo desde el README:

```
🔗 Demo en vivo: https://auth-service.tudominio.com/docs
```

Cualquier reclutador puede abrir esa URL, ver la documentación interactiva,
y probar los endpoints en tiempo real sin instalar nada.