from django.core.management.base import BaseCommand
from shapely.geometry import Polygon
from core.models import Field
from core.views import generate_compaction_heatmap_points, save_compaction_heatmap_points


class Command(BaseCommand):
    help = "Generate compaction heatmap points for every field using existing Run data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optionally limit how many fields to process (for testing).",
        )

    def handle(self, *args, **options):
        limit = options.get("limit")
        fields = Field.objects.all()

        if limit:
            fields = fields[:limit]

        total_fields = fields.count()
        if total_fields == 0:
            self.stdout.write(self.style.WARNING("No fields found in the database."))
            return

        self.stdout.write(self.style.HTTP_INFO(f"Generating compaction heatmaps for {total_fields} field(s)...\n"))

        for field in fields:
            self._process_field(field)

        self.stdout.write(self.style.SUCCESS("\n✅ All compaction heatmaps generated successfully."))

    # ----------------------------------------------------------------------
    # Helper function
    # ----------------------------------------------------------------------
    def _process_field(self, field):
        self.stdout.write(self.style.HTTP_INFO(f"→ Processing field: {field.name} ({field.id})"))

        poly = Polygon(field.boundary)
        feature_collection, points = generate_compaction_heatmap_points(field.boundary)

        if points:
            save_compaction_heatmap_points(field, points)
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ Generated {len(points)} compaction heatmap points for '{field.name}'."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"   ⚠ No compaction data found within '{field.name}' boundary."
                )
            )
