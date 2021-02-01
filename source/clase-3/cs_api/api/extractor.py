from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import pytz
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Extrae y valida los headers de paginación
def extract_paging_from_request(request, page_default=1, page_size_default=6):
    try:
        page = int(request.GET.get('p', page_default))
        page_size = int(request.GET.get('s', page_size_default))
    except ValueError:
        return None, None, Response(status=status.HTTP_400_BAD_REQUEST)
    return page, page_size, None

# Extrae y valida los query params de fechas
def extract_limits_from_request(request, limit_low_default=None, limit_high_default=datetime.now()):
    if limit_low_default == None:
        limit_low_default = request.user.date_joined
    try:
        # Extraemos como strings con default None
        inicio_str = request.GET.get('inicio', None)
        fin_str = request.GET.get('fin', None)
        # Si ninguno vino, devolvemos None
        if inicio_str == None and fin_str == None:
            return None, None, None
        # Convertimos cada uno
        if inicio_str == None:
            inicio = limit_low_default
        else:
            inicio = datetime.strptime(inicio_str, DATE_FORMAT)
        if fin_str == None:
            fin = limit_high_default
        else:
            fin = datetime.strptime(fin_str, DATE_FORMAT)
    except ValueError:
        return None, None, Response(status=status.HTTP_400_BAD_REQUEST)
    return pytz.utc.localize(inicio), pytz.utc.localize(fin), None