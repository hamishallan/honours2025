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

    def handle(self, *args, **options):
        field_id = options["field_id"]
        num_points = options["num"]

        try:
            field = Field.objects.get(id=field_id)
        except Field.DoesNotExist:
            self.stderr.write(self.style.ERROR("Field not found"))
            return

        poly = Polygon(field.boundary)

        # Estimate grid size (rows × cols ~ num_points)
        num_cols = int(num_points ** 0.5)
        num_rows = int(num_points / num_cols)

        minx, miny, maxx, maxy = poly.bounds
        dx = (maxx - minx) / (num_cols - 1)
        dy = (maxy - miny) / (num_rows - 1)

        self.stdout.write(
            self.style.HTTP_INFO(f"Creating predictions...")
        )

        created = 0
        for i in range(num_cols):
            for j in range(num_rows):
                if created >= num_points:
                    break

                # Grid position
                lon = minx + i * dx
                lat = miny + j * dy

                # Add jitter so it's not a perfect grid
                lon += random.uniform(-dx * 0.2, dx * 0.2)
                lat += random.uniform(-dy * 0.2, dy * 0.2)

                pt = Point(lon, lat)
                if poly.contains(pt):
                    # ----- Weighted value generation -----
                    rel_x = (lon - minx) / (maxx - minx)

                    # Base gradient: higher SOC west → lower east
                    base_value = 6.0 - (rel_x * 4.0)  # ~6% to ~2%

                    # Add random variation (soil heterogeneity)
                    noise = random.gauss(0, 0.3)

                    soc_value = max(1.5, min(6.0, base_value + noise))

                    # ----- Save -----
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
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} fake predictions inside {field.name}")
        )
        
        self.stdout.write(
            self.style.HTTP_INFO(f"Generating heatmap...")
        )

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
