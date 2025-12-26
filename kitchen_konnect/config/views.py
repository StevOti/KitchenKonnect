from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token


@ensure_csrf_cookie
def csrf_token_view(request):
    """Return a JSON response with the current CSRF token and ensure the cookie is set."""
    return JsonResponse({'csrfToken': get_token(request)})
