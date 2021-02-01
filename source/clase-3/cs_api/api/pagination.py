# Importamos para parsear la url
import urllib.parse as urlparse
# Importamos nuestras constantes
from api import constants

# Agrega headers de paginación a la response
def add_paging_to_response(request, response, query_data, page, total_pages):
    # Extraemos la URL
    complete_url = request.build_absolute_uri()
    # Usamos un pequeño "algoritmo" para determinar que headers mostrar
    # Si tiene próxima, la agrego
    if query_data.has_next():
        response[constants.HEADER_NEXT] = replace_page_param(
            complete_url, query_data.next_page_number())
    # Si tiene anterior, la agrego
    if query_data.has_previous():
        response[constants.HEADER_PREV] = replace_page_param(
            complete_url, query_data.previous_page_number())
    # Si no estamos en la última página, y tampoco en la anteúltima, lo agrego
    if page < total_pages and (query_data.has_next() and query_data.next_page_number() != total_pages):
        response[constants.HEADER_LAST] = replace_page_param(
            complete_url, total_pages)
    # Si no estamos en la página 1 y tiene una página anterior que es diferente de 1, la agregamos
    if page > 1 and (query_data.has_previous() and query_data.previous_page_number() != 1):
        response[constants.HEADER_FIRST] = replace_page_param(complete_url, 1)
    return response

# Reemplaza el parámetro de la p en la url dada
def replace_page_param(url, new_page):
    # Parseamos la URL
    parsed = urlparse.urlparse(url)
    # Extraemos los query params
    querys = parsed.query.split("&")
    # Flag para ver si vino o no el param de la página
    has_page = False
    # Buscamos el param de la página
    for i in range(len(querys)):
        # Separamos para ver si empieza con "p"
        parts = querys[i].split('=')
        if parts[0] == 'p':
            # Cambiamos el parámetro viejo por el nuevo
            querys[i] = 'p=' + str(new_page)
            has_page = True

    # Si no vino con página lo agregamos
    if not has_page:
        querys.append("p=" + str(new_page))

    # Reconstruimos los query params
    new_query = "&".join(["{}".format(query) for query in querys])
    # Reconstruimos la URL
    parsed = parsed._replace(query=new_query)

    return urlparse.urlunparse(parsed)