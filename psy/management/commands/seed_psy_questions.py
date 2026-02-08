from django.core.management.base import BaseCommand

from psy.models import PsyQuestion


DEFAULT_QUESTIONS = [
    "나는 새로운 사람을 만나는 것을 즐긴다.",
    "나는 계획을 세우기보다 즉흥적으로 행동하는 편이다.",
    "나는 스트레스를 받으면 쉽게 피로해진다.",
    "나는 팀에서 의견을 적극적으로 말하는 편이다.",
    "나는 혼자 있는 시간도 중요하게 생각한다.",
]


class Command(BaseCommand):
    help = "Seed 50 psy questions (PoC)"

    def handle(self, *args, **options):
        if PsyQuestion.objects.exists():
            self.stdout.write(self.style.WARNING("PsyQuestion already exists; skipping"))
            return

        questions = []
        for i in range(1, 51):
            text = DEFAULT_QUESTIONS[(i - 1) % len(DEFAULT_QUESTIONS)]
            questions.append(
                PsyQuestion(
                    code=f"Q{i}",
                    text=text,
                    order_index=i,
                    scale_min=1,
                    scale_max=5,
                    reverse_scored=False,
                )
            )

        PsyQuestion.objects.bulk_create(questions)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(questions)} psy questions"))
