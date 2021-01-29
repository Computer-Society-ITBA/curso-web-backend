from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def test_get(request):
    return Response({"hello": "world"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_get_path_param(request, id):
    return Response({"hello": id}, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_get_query_param(request):
    q = request.GET.get('q', 'default')
    return Response({"hello": q}, status=status.HTTP_200_OK)

@api_view(['POST'])
def test_post_body(request):
    return Response({"hello": request.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_get_sum(request):
    l = float(request.GET.get('l', 0.0))
    r = float(request.GET.get('r', 0.0))
    return Response({"resultado": l + r}, status=status.HTTP_200_OK)

@api_view(['PUT'])
def test_get_sum_mas(request):
    nums = request.data["sums"]
    sum = 0
    for n in nums:
        sum += n
    return Response({"resultado": sum}, status=status.HTTP_200_OK)

@api_view(['POST'])
def test_bueno(request):
    limit = float(request.GET.get('limit', 10.0))
    n = float(request.data["n"])
    if n >= limit:
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)