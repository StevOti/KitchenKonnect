from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
	"""Custom user extending Django's AbstractUser.

	- `email` is unique and used as a primary contact field.
	- `dietary_preferences` stores structured user preferences (JSON).
	- `bio` is a short user-provided description.
	"""

	email = models.EmailField('email address', unique=True)
	dietary_preferences = models.JSONField(blank=True, null=True, default=dict)
	bio = models.TextField(blank=True)

	def __str__(self) -> str:  # keep signature simple and explicit
		return self.username
