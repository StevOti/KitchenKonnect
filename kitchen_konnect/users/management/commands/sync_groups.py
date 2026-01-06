from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Sync Django Group membership from CustomUser.role field (groups: users, regulators, admins)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would change without applying')
        parser.add_argument('--username', type=str, help='Only sync a single username')

    def handle(self, *args, **options):
        User = get_user_model()
        dry = options.get('dry_run', False)
        username = options.get('username')

        users_qs = User.objects.all().order_by('id')
        if username:
            users_qs = users_qs.filter(username=username)

        users_grp, _ = Group.objects.get_or_create(name='users')
        regs_grp, _ = Group.objects.get_or_create(name='regulators')
        admins_grp, _ = Group.objects.get_or_create(name='admins')

        changed = 0
        for u in users_qs:
            target = None
            try:
                role = getattr(u, 'role', None)
            except Exception:
                role = None
            if role == getattr(User, 'ROLE_ADMIN', 'admin'):
                target = admins_grp
            elif role == getattr(User, 'ROLE_REGULATOR', 'regulator'):
                target = regs_grp
            else:
                # both regular and nutritionist fall into 'users' group
                target = users_grp

            current = set(u.groups.all())
            desired = {target}

            if current != desired:
                changed += 1
                if dry:
                    self.stdout.write(self.style.WARNING(f'[DRY] {u.username}: would set groups -> {[g.name for g in desired]} (was {[g.name for g in current]})'))
                else:
                    try:
                        u.groups.set(list(desired))
                        u.save()
                        self.stdout.write(self.style.SUCCESS(f'{u.username}: groups set -> {[g.name for g in desired]}'))
                    except Exception as e:
                        self.stderr.write(f'Error updating {u.username}: {e}')

        self.stdout.write(self.style.NOTICE(f'Done. {changed} user(s) changed.'))
