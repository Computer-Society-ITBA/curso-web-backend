---
layout: default
title:  "Requests"
description: "Ejemplos de Requests"
principal: false
---

# Clase Requests

¡Bienvenidos al Curso de Web Backend!

Acá pueden encontrar ejemplos para todas las requests que vamos a usar durante el curso. Es una recopilación para que sea más cómodo encontrar que requests hay.

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

### Borrar usuario:
```bash
curl -X DELETE -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts/1
```

### Listar usuarios:
```bash
curl -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts?p=P&s=S
```

### Filtrar usuarios:
```bash
curl -H "Authorization: JWT TOKEN" http://localhost:8000/api/accounts?q=BUSQUEDA&p=P&s=S
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
