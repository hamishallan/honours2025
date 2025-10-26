from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Spectrum, Run
import random


class Command(BaseCommand):
    help = "Bulk-create Run entries for all Spectrum records, linking and copying lat/long."

    def handle(self, *args, **options):
        spectra = Spectrum.objects.all()
        total = spectra.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No Spectrum records found."))
            return

        self.stdout.write(self.style.HTTP_INFO(f"Fetching existing run IDs..."))
        existing_ids = set(Run.objects.values_list("spectrum_id", flat=True))

        self.stdout.write(self.style.HTTP_INFO(f"Preparing new runs for bulk insert..."))
        new_runs = []
        now = timezone.now()

        for s in spectra.iterator():  # iterator() to reduce memory footprint
            if s.id in existing_ids:
                continue

            new_runs.append(
                Run(
                    spectrum=s,
                    latitude=s.latitude,
                    longitude=s.longitude,
                    predicted_soc=round(random.uniform(1.0, 7.0), 2),
                    max_depth_mm=round(random.uniform(50, 300), 2),
                    max_weight_kg=round(random.uniform(1.0, 10.0), 2),
                    compaction_pa=round(random.uniform(10000, 50000), 2),
                    timestamp=now,
                )
            )

        if not new_runs:
            self.stdout.write(self.style.WARNING("All spectra already have runs. Nothing to create."))
            return

        self.stdout.write(self.style.HTTP_INFO(f"Bulk inserting {len(new_runs)} new runs..."))
        Run.objects.bulk_create(new_runs, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"Inserted {len(new_runs)} runs successfully."))
