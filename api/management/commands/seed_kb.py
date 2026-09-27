from django.core.management.base import BaseCommand

from api.models import KBEntry


ENTRIES = [
    ('What is select_related in Django ORM?', 'select_related performs a SQL JOIN for related foreign key objects.', 'database'),
    ('When should I use prefetch_related?', 'prefetch_related loads many-to-many and reverse relations in separate queries.', 'database'),
    ('How does transaction.atomic work?', 'transaction.atomic groups database operations so they commit or roll back together.', 'database'),
    ('What is a JWT token?', 'A JWT is a signed token containing claims used to authenticate API requests.', 'api'),
    ('How do I secure an API?', 'Use TLS, strong authentication, authorization, validation, and rate limiting.', 'api'),
    ('What is a REST API?', 'A REST API exposes resources over HTTP using standard methods and representations.', 'api'),
    ('What is cloud autoscaling?', 'Autoscaling adjusts compute capacity based on demand and configured policies.', 'cloud'),
    ('What is a Docker container?', 'A container packages an application and its dependencies into an isolated process.', 'cloud'),
    ('What is dependency injection?', 'Dependency injection supplies a component with its dependencies instead of constructing them internally.', 'framework'),
    ('What are Q objects in Django?', 'Q objects compose complex database filters using AND, OR, and NOT logic.', 'framework'),
]


class Command(BaseCommand):
    help = 'Seed the knowledge base with starter entries.'

    def handle(self, *args, **options):
        created = 0
        for question, answer, category in ENTRIES:
            _, was_created = KBEntry.objects.get_or_create(
                question=question,
                defaults={'answer': answer, 'category': category},
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f'Created {created} KB entries.'))