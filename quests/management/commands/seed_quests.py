from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from quests.models import QuestTemplate, UserQuest


DAILY_TEMPLATES = [
    ("오늘 30분 이상 걷기", "가벼운 산책으로 몸을 풀어보세요."),
    ("감사 일기 3줄 쓰기", "오늘 있었던 좋은 일 3가지를 적어보세요."),
    ("물 6잔 마시기", "수분 섭취로 컨디션을 관리해보세요."),
]

WEEKLY_TEMPLATES = [
    ("이번 주에 친구 1명에게 연락하기", "오래 연락하지 못한 친구에게 근황을 전해보세요."),
]


class Command(BaseCommand):
    help = "Seed quest templates and assign today's quests to a user (PoC)"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="user@example.com")

    def handle(self, *args, **options):
        email = options["email"]
        sub = f"dummy-{email}"
        user, _ = User.objects.get_or_create(
            cognito_sub=sub,
            defaults={"email": email, "name": ""},
        )

        if not QuestTemplate.objects.exists():
            templates = []
            for title, desc in DAILY_TEMPLATES:
                templates.append(QuestTemplate(title=title, description=desc, type="daily", is_active=True))
            for title, desc in WEEKLY_TEMPLATES:
                templates.append(QuestTemplate(title=title, description=desc, type="weekly", is_active=True))
            QuestTemplate.objects.bulk_create(templates)
            self.stdout.write(self.style.SUCCESS(f"Seeded {len(templates)} quest templates"))

        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

        daily_templates = QuestTemplate.objects.filter(type="daily", is_active=True).order_by("id")[:3]
        weekly_template = QuestTemplate.objects.filter(type="weekly", is_active=True).order_by("id").first()

        created = 0
        for tpl in daily_templates:
            obj, was_created = UserQuest.objects.get_or_create(
                user=user,
                quest_template=tpl,
                period_date=today,
                defaults={"status": "pending"},
            )
            created += 1 if was_created else 0

        if weekly_template:
            obj, was_created = UserQuest.objects.get_or_create(
                user=user,
                quest_template=weekly_template,
                week_start_date=week_start,
                defaults={"status": "pending"},
            )
            created += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Ensured quests for {email}. Newly created: {created}"))
