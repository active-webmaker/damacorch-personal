from django.core.management.base import BaseCommand

from sns_integration.models import SnsChannel


CHANNELS = [
    ("instagram", "인스타그램"),
    ("kakao", "카카오톡"),
    ("facebook", "페이스북"),
]


class Command(BaseCommand):
    help = "Seed SNS channels (PoC)"

    def handle(self, *args, **options):
        created = 0
        for code, name in CHANNELS:
            _obj, was_created = SnsChannel.objects.get_or_create(
                code=code,
                defaults={"name": name, "icon_url": "", "is_active": True},
            )
            created += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} sns channels"))
