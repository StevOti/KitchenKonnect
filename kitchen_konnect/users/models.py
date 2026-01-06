from django.db import models
from django.contrib.auth.models import AbstractUser, Group


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
		# If object is marked superuser (created via createsuperuser), ensure
		# role reflects that and admin_level is high.
		if self.is_superuser:
			self.role = self.ROLE_ADMIN
			self.is_staff = True
			if (not self.admin_level) or (self.admin_level < 100):
				self.admin_level = 100
		elif self.role == self.ROLE_ADMIN:
			self.is_staff = True
			# convention: admin_level >= 100 -> superuser
			if self.admin_level >= 100:
				self.is_superuser = True
		elif self.role == self.ROLE_REGULATOR:
			# Regulators receive a minimum admin level so they can access
			# regulator/admin-level endpoints. Preserve any higher level.
			if (not self.admin_level) or (self.admin_level < 50):
				self.admin_level = 50
		super_ret = super().save(*args, **kwargs)

		# Ensure group membership mirrors role grouping used by the app.
		# Groups: 'users' (default), 'regulators', 'admins'
		try:
			users_grp, _ = Group.objects.get_or_create(name='users')
			regs_grp, _ = Group.objects.get_or_create(name='regulators')
			admins_grp, _ = Group.objects.get_or_create(name='admins')

			if self.role == self.ROLE_ADMIN:
				self.groups.set([admins_grp])
			elif self.role == self.ROLE_REGULATOR:
				self.groups.set([regs_grp])
			else:
				# regular and nutritionist users belong to the 'users' group
				self.groups.set([users_grp])
		except Exception:
			# Avoid raising errors on group management during migrations or
			# when auth tables may not be ready.
			pass

		return super_ret


class VerificationRequest(models.Model):
	"""A request by a user to be verified as a nutritionist, regulator, or admin.

	Admins review and approve/reject these requests.
	"""

	STATUS_PENDING = 'pending'
	STATUS_APPROVED = 'approved'
	STATUS_REJECTED = 'rejected'

	STATUS_CHOICES = (
		(STATUS_PENDING, 'Pending'),
		(STATUS_APPROVED, 'Approved'),
		(STATUS_REJECTED, 'Rejected'),
	)

	REQUEST_NUTRITIONIST = CustomUser.ROLE_NUTRITIONIST
	REQUEST_REGULATOR = CustomUser.ROLE_REGULATOR
	REQUEST_ADMIN = CustomUser.ROLE_ADMIN

	REQUEST_CHOICES = (
		(REQUEST_NUTRITIONIST, 'Nutritionist'),
		(REQUEST_REGULATOR, 'Regulator'),
		(REQUEST_ADMIN, 'Admin'),
	)

	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_requests')
	requested_role = models.CharField(max_length=20, choices=REQUEST_CHOICES)
	message = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	reviewed_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_verifications')
	reviewed_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self) -> str:
		return f"{self.user.username} -> {self.requested_role} ({self.status})"
