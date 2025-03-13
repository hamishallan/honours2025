from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()  # Fetch all users
    serializer = UserSerializer(users, many=True)
    return Response({"users": serializer.data})