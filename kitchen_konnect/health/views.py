from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ProtectedHealthView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response({'detail': 'This is a protected health endpoint', 'user': request.user.username})
