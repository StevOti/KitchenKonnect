from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ProtectedRecipeView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response({'detail': 'This is a protected recipe endpoint', 'user': request.user.username})
