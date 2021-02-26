---
layout: default
title:  "Requests"
description: "Ejemplos de Requests"
principal: false
active: true
---

# Clase Requests

¡Bienvenidos al Curso de Web Backend!

Acá pueden encontrar ejemplos para todas las requests que vamos a usar durante el curso. Es una recopilación para que sea más cómodo encontrar que requests hay.

La URL de la API de producción es: https://csitba.azurewebsites.net

Requests:

## Auth

### Login:
```bash
curl -X POST -d 'username=USERNAME&password=PASSWORD' http://localhost:8000/api/auth/login
```

## Usuarios

### Crear un usuario
```bash
curl -X POST -F 'username=USERNAME' -F 'email=EMAIL' -F 'password1=PASSWORD' -F 'password2=PASSWORD' http://localhost:8000/api/accounts
```

### Listar usuarios:
```bash
curl -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts?p=P&s=S
```

### Filtrar usuarios:
```bash
curl -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts?q=BUSQUEDA&p=P&s=S
```

### Perfil de usuario
```bash
curl -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts/ID
```

### Borrar usuario:
```bash
curl -X DELETE -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts/ID
```

### Actualizar usuario
Sirve para cambiar el balance o el rol:
```bash
curl -i -X PUT -H "Authorization: JWT TOKEN" -H "Content-Type: application/json" http://localhost:8000/api/accounts/ID -d '{"balance": BALANCE,"email": "EMAIL","groups": [{"name": "GRUPO"}],"id": ID,"username": "USERNAME"}'
```

### Verificar usuario
Sirve con el link que viene en el mail:
```bash
curl -i LINK_DEL_MAIL
```

## Transacciones

### Crear transacción:
```bash
curl -X POST -H "Authorization: JWT TOKEN" -F 'destino=DESTINO_ID' -F 'cantidad=CANTIDAD' http://localhost:8000/api/transactions
```

### Listar transacciones:
```bash
curl -H "Authorization: JWT TOKEN" http://localhost:8000/api/transactions?p=P&s=S
```

### Buscar transacciones:
```bash
curl -G -H "Authorization: JWT TOKEN" --data-urlencode "inicio=INICIO" --data-urlencode "fin=FIN" 'http://localhost:8000/api/transactions?p=P&s=S'
```