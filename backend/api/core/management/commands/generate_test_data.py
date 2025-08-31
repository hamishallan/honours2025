from django.core.management.base import BaseCommand
from django.utils import timezone
import random
from shapely.geometry import Point, Polygon
from core.models import Field, Spectrum, Prediction
from core.views import generate_heatmap_points, save_heatmap_points


class Command(BaseCommand):
    help = "Generate fake SOC predictions inside a field and regenerate its heatmap"

    def add_arguments(self, parser):
        parser.add_argument("field_id", type=str, help="UUID of the field")
        parser.add_argument(
            "--num", type=int, default=100, help="Approximate number of points to generate"
        )
        parser.add_argument(
            "--mode",
            type=str,
            choices=["grid", "random"],
            default="random",
            help="Point generation mode: grid (east–west gradient) or random (uniform)",
        )

    def handle(self, *args, **options):
        field_id = options["field_id"]
        num_points = options["num"]
        mode = options["mode"]

        try:
            field = Field.objects.get(id=field_id)
        except Field.DoesNotExist:
            self.stderr.write(self.style.ERROR("Field not found"))
            return

        poly = Polygon(field.boundary)

        self.stdout.write(self.style.HTTP_INFO(f"Creating predictions in {mode} mode..."))

        created = 0
        minx, miny, maxx, maxy = poly.bounds

        if mode == "grid":
            # -------- Grid-based generation (east–west gradient) --------
            num_cols = int(num_points ** 0.5)
            num_rows = int(num_points / num_cols)

            dx = (maxx - minx) / (num_cols - 1)
            dy = (maxy - miny) / (num_rows - 1)

            for i in range(num_cols):
                for j in range(num_rows):
                    if created >= num_points:
                        break

                    lon = minx + i * dx + random.uniform(-dx * 0.2, dx * 0.2)
                    lat = miny + j * dy + random.uniform(-dy * 0.2, dy * 0.2)

                    pt = Point(lon, lat)
                    if poly.contains(pt):
                        created += self._create_prediction_grid(lon, lat, minx, maxx)

        else:
            # -------- Purely random points (uniform SOC values) --------
            while created < num_points:
                lon = random.uniform(minx, maxx)
                lat = random.uniform(miny, maxy)
                pt = Point(lon, lat)
                if poly.contains(pt):
                    created += self._create_prediction_random(lon, lat)

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} fake predictions inside {field.name}")
        )

        self.stdout.write(self.style.HTTP_INFO(f"Generating heatmap..."))

        # ---- Regenerate heatmap after inserting test data ----
        feature_collection, points = generate_heatmap_points(field.boundary)
        if points:
            save_heatmap_points(field, points)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Heatmap regenerated for {field.name} with {len(points)} grid cells"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"No heatmap points generated for {field.name}")
            )

    # ----------------------------------------------------------------------
    # Helper functions for SOC value generation + saving
    # ----------------------------------------------------------------------
    def _create_prediction_grid(self, lon, lat, minx, maxx):
        # East–west gradient: high in west → low in east
        rel_x = (lon - minx) / (maxx - minx)
        base_value = 6.0 - (rel_x * 4.0)   # ~6% west → ~2% east
        noise = random.gauss(0, 0.3)
        soc_value = max(1.5, min(6.0, base_value + noise))
        self._save_prediction(lon, lat, soc_value)
        return 1

    def _create_prediction_random(self, lon, lat):
        # Uniform random in [2.0, 6.0]
        soc_value = random.uniform(2.0, 6.0)
        self._save_prediction(lon, lat, soc_value)
        return 1

    def _save_prediction(self, lon, lat, soc_value):
        spectrum = Spectrum.objects.create(
            device_id="test-device",
            latitude=lat,
            longitude=lon,
            altitude_m=50.0,
            accuracy_m=1.0,
        )
        Prediction.objects.create(
            spectrum=spectrum,
            predicted_value=round(soc_value, 2),
            timestamp=timezone.now(),
        )
