from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create 1000 users with username and password as UserNumber<index>'

    def handle(self, *args, **kwargs):
        users = []
        for i in range(1, 20):
            username = f'User{i}'
            password = username
            email = f'{username}@example.com'

            user = User(
                username=username,
                email=email
            )
            user.set_password(password)
            users.append(user)

        User.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS('Successfully created 1000 users'))
