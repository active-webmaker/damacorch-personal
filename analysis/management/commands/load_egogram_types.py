import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from analysis.models import EgogramType


class Command(BaseCommand):
    help = "Load egogram types from docs/egogram_type.csv"

    def add_arguments(self, parser):
        parser.add_argument("--csv", dest="csv_path", default=str(Path("docs") / "egogram_type.csv"))

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise FileNotFoundError(str(csv_path))

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if "유형" not in reader.fieldnames or "해석" not in reader.fieldnames:
                raise ValueError(f"Unexpected CSV headers: {reader.fieldnames}")

            count = 0
            for row in reader:
                code = (row.get("유형") or "").strip()
                interpretation = (row.get("해석") or "").strip()
                if not code:
                    continue

                EgogramType.objects.update_or_create(
                    code=code,
                    defaults={"interpretation": interpretation},
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {count} egogram types"))
