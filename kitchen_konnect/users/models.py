from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
	"""Custom user extending Django's AbstractUser.

	Roles and admin levels
	- `role` divides users into categories: regular, nutritionist, admin, regulator.
	- `admin_level` is an integer rank used to create hierarchy among admins
	  (higher value => higher privileges). The application may map levels to
	  different capabilities; by convention a very high `admin_level` (e.g. >=100)
	  may be treated as superuser-equivalent.

	Other fields:
	- `email` is unique and used as a primary contact field.
	- `dietary_preferences` stores structured user preferences (JSON).
	- `bio` is a short user-provided description.
	"""

	ROLE_REGULAR = 'regular'
	ROLE_NUTRITIONIST = 'nutritionist'
	ROLE_ADMIN = 'admin'
	ROLE_REGULATOR = 'regulator'

	ROLE_CHOICES = (
		(ROLE_REGULAR, 'Regular'),
		(ROLE_NUTRITIONIST, 'Nutritionist'),
		(ROLE_ADMIN, 'Admin'),
		(ROLE_REGULATOR, 'Regulator'),
	)

	email = models.EmailField('email address', unique=True)
	dietary_preferences = models.JSONField(blank=True, null=True, default=dict)
	bio = models.TextField(blank=True)

	# Role and admin hierarchy
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_REGULAR)
	# admin_level gives ordering among admin users; non-admins may keep 0
	admin_level = models.PositiveSmallIntegerField(default=0)

	def __str__(self) -> str:
		return self.username

	# convenience helpers
	def is_nutritionist(self) -> bool:
		return self.role == self.ROLE_NUTRITIONIST

	def is_regulator(self) -> bool:
		return self.role == self.ROLE_REGULATOR

	def is_regular(self) -> bool:
		return self.role == self.ROLE_REGULAR

	def is_admin(self) -> bool:
		return self.role == self.ROLE_ADMIN

	@property
	def admin_rank(self) -> int:
		return int(self.admin_level or 0)

	def save(self, *args, **kwargs):
		# Ensure admin users get staff status; very high admin_level can imply
		# superuser privileges (application-level convention). We avoid
		# unsetting existing superuser flags to prevent accidental privilege
		# removal.
		if self.role == self.ROLE_ADMIN:
			self.is_staff = True
			# convention: admin_level >= 100 -> superuser
			if self.admin_level >= 100:
				self.is_superuser = True
		return super().save(*args, **kwargs)
