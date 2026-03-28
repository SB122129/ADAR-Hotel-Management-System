import base64
import io
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from Hall.models import Hall, Hall_Category
from Spa.models import SpaPackage, SpaService
from gym.models import MembershipPlan
from room.models import Category, Room


class Command(BaseCommand):
    help = (
        "Populate sample rooms, halls, membership plans, spa services, and "
        "spa packages with placeholder images."
    )

    # 1x1 PNG used as a fallback when PIL is unavailable.
    FALLBACK_PNG = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7+WJ0AAAAASUVORK5CYII="
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace-images",
            action="store_true",
            help="Regenerate and replace existing sample images.",
        )

    def handle(self, *args, **options):
        replace_images = options["replace_images"]
        summary = {
            "Room Categories": {"created": 0, "updated": 0, "images": 0},
            "Rooms": {"created": 0, "updated": 0, "images": 0},
            "Hall Categories": {"created": 0, "updated": 0, "images": 0},
            "Halls": {"created": 0, "updated": 0, "images": 0},
            "Membership Plans": {"created": 0, "updated": 0, "images": 0},
            "Spa Services": {"created": 0, "updated": 0, "images": 0},
            "Spa Packages": {"created": 0, "updated": 0, "images": 0},
        }

        with transaction.atomic():
            room_categories = self._seed_room_categories(summary)
            self._seed_rooms(room_categories, summary, replace_images)

            hall_categories = self._seed_hall_categories(summary)
            self._seed_halls(hall_categories, summary, replace_images)

            self._seed_membership_plans(summary)
            self._seed_spa_services(summary, replace_images)
            self._seed_spa_packages(summary, replace_images)

        self.stdout.write(self.style.SUCCESS("Sample data seeding complete."))
        for label, counts in summary.items():
            self.stdout.write(
                f"- {label}: created={counts['created']}, "
                f"updated={counts['updated']}, images={counts['images']}"
            )

    def _seed_room_categories(self, summary):
        category_rows = [
            {"name": "Sample Standard", "rank": 1},
            {"name": "Sample Deluxe", "rank": 2},
            {"name": "Sample Family Suite", "rank": 3},
            {"name": "Sample Presidential", "rank": 4},
        ]

        category_map = {}
        for row in category_rows:
            category, created = Category.objects.update_or_create(
                name=row["name"],
                defaults={"rank": row["rank"]},
            )
            self._track(summary, "Room Categories", created)
            category_map[row["name"]] = category

        return category_map

    def _seed_rooms(self, room_categories, summary, replace_images):
        room_rows = [
            {
                "room_number": "S101",
                "room_type": "Sample Standard",
                "price_per_night": Decimal("95.00"),
                "discount": Decimal("5.00"),
                "room_status": "vacant",
                "capacity": 2,
                "description": "Sample standard room with city-facing windows.",
                "floor": 1,
                "color": "#4F8EF7",
            },
            {
                "room_number": "S102",
                "room_type": "Sample Standard",
                "price_per_night": Decimal("90.00"),
                "discount": None,
                "room_status": "occupied",
                "capacity": 2,
                "description": "Sample standard room near elevator access.",
                "floor": 1,
                "color": "#5CA9FF",
            },
            {
                "room_number": "S201",
                "room_type": "Sample Deluxe",
                "price_per_night": Decimal("140.00"),
                "discount": Decimal("10.00"),
                "room_status": "vacant",
                "capacity": 3,
                "description": "Sample deluxe room with balcony and lounge chair.",
                "floor": 2,
                "color": "#2F6AA3",
            },
            {
                "room_number": "S202",
                "room_type": "Sample Deluxe",
                "price_per_night": Decimal("150.00"),
                "discount": Decimal("12.50"),
                "room_status": "vacant",
                "capacity": 3,
                "description": "Sample deluxe room with mountain view.",
                "floor": 2,
                "color": "#3B8D99",
            },
            {
                "room_number": "S301",
                "room_type": "Sample Family Suite",
                "price_per_night": Decimal("220.00"),
                "discount": Decimal("15.00"),
                "room_status": "occupied",
                "capacity": 5,
                "description": "Sample family suite with connected living area.",
                "floor": 3,
                "color": "#4A7C59",
            },
            {
                "room_number": "S401",
                "room_type": "Sample Presidential",
                "price_per_night": Decimal("450.00"),
                "discount": Decimal("50.00"),
                "room_status": "vacant",
                "capacity": 6,
                "description": "Sample presidential suite with premium amenities.",
                "floor": 4,
                "color": "#7F5539",
            },
        ]

        for row in room_rows:
            room, created = Room.objects.update_or_create(
                room_number=row["room_number"],
                defaults={
                    "room_type": room_categories[row["room_type"]],
                    "price_per_night": row["price_per_night"],
                    "discount": row["discount"],
                    "room_status": row["room_status"],
                    "capacity": row["capacity"],
                    "description": row["description"],
                    "floor": row["floor"],
                },
            )
            self._track(summary, "Rooms", created)

            if self._attach_placeholder_image(
                instance=room,
                field_name="room_image",
                filename=f"sample_room_{slugify(row['room_number'])}.png",
                color=row["color"],
                replace=replace_images,
            ):
                summary["Rooms"]["images"] += 1

    def _seed_hall_categories(self, summary):
        category_rows = [
            "Sample Conference",
            "Sample Wedding",
            "Sample Banquet",
            "Sample Boardroom",
        ]

        category_map = {}
        for name in category_rows:
            category, created = Hall_Category.objects.update_or_create(name=name, defaults={})
            self._track(summary, "Hall Categories", created)
            category_map[name] = category

        return category_map

    def _seed_halls(self, hall_categories, summary, replace_images):
        hall_rows = [
            {
                "hall_number": "SH-201",
                "hall_type": "Sample Conference",
                "description": "Sample conference hall with projector and stage.",
                "price_per_hour": Decimal("120.00"),
                "capacity": 120,
                "floor": 2,
                "status": "available",
                "color": "#1F6F8B",
            },
            {
                "hall_number": "SH-202",
                "hall_type": "Sample Boardroom",
                "description": "Sample boardroom hall for executive meetings.",
                "price_per_hour": Decimal("80.00"),
                "capacity": 40,
                "floor": 2,
                "status": "booked",
                "color": "#335C67",
            },
            {
                "hall_number": "SH-301",
                "hall_type": "Sample Wedding",
                "description": "Sample wedding hall with open floor arrangement.",
                "price_per_hour": Decimal("200.00"),
                "capacity": 250,
                "floor": 3,
                "status": "available",
                "color": "#9A031E",
            },
            {
                "hall_number": "SH-302",
                "hall_type": "Sample Banquet",
                "description": "Sample banquet hall suitable for formal dinners.",
                "price_per_hour": Decimal("170.00"),
                "capacity": 180,
                "floor": 3,
                "status": "available",
                "color": "#6A4C93",
            },
        ]

        for row in hall_rows:
            hall, created = Hall.objects.update_or_create(
                hall_number=row["hall_number"],
                defaults={
                    "hall_type": hall_categories[row["hall_type"]],
                    "description": row["description"],
                    "price_per_hour": row["price_per_hour"],
                    "capacity": row["capacity"],
                    "floor": row["floor"],
                    "status": row["status"],
                },
            )
            self._track(summary, "Halls", created)

            if self._attach_placeholder_image(
                instance=hall,
                field_name="image",
                filename=f"sample_hall_{slugify(row['hall_number'])}.png",
                color=row["color"],
                replace=replace_images,
            ):
                summary["Halls"]["images"] += 1

    def _seed_membership_plans(self, summary):
        plan_rows = [
            {
                "name": "Sample Bronze Monthly",
                "price": Decimal("120.00"),
                "duration_months": 1,
                "description": "Sample basic membership plan for monthly access.",
            },
            {
                "name": "Sample Silver Quarterly",
                "price": Decimal("330.00"),
                "duration_months": 3,
                "description": "Sample quarterly plan with trainer check-ins.",
            },
            {
                "name": "Sample Gold Semiannual",
                "price": Decimal("620.00"),
                "duration_months": 6,
                "description": "Sample six-month plan including group classes.",
            },
            {
                "name": "Sample Platinum Annual",
                "price": Decimal("1150.00"),
                "duration_months": 12,
                "description": "Sample full-year premium plan with all facilities.",
            },
        ]

        for row in plan_rows:
            _, created = MembershipPlan.objects.update_or_create(
                name=row["name"],
                defaults={
                    "price": row["price"],
                    "duration_months": row["duration_months"],
                    "description": row["description"],
                },
            )
            self._track(summary, "Membership Plans", created)

    def _seed_spa_services(self, summary, replace_images):
        service_rows = [
            {
                "name": "Sample Swedish Massage",
                "description": "Sample calming full-body massage service.",
                "price": Decimal("70.00"),
                "color": "#F4A261",
            },
            {
                "name": "Sample Deep Tissue Massage",
                "description": "Sample targeted deep tissue recovery massage.",
                "price": Decimal("85.00"),
                "color": "#E76F51",
            },
            {
                "name": "Sample Aromatherapy Session",
                "description": "Sample aroma-based stress relief treatment.",
                "price": Decimal("65.00"),
                "color": "#2A9D8F",
            },
            {
                "name": "Sample Facial Treatment",
                "description": "Sample skin-refreshing facial treatment.",
                "price": Decimal("55.00"),
                "color": "#E9C46A",
            },
        ]

        for row in service_rows:
            service, created = SpaService.objects.update_or_create(
                name=row["name"],
                defaults={
                    "description": row["description"],
                    "price": row["price"],
                },
            )
            self._track(summary, "Spa Services", created)

            if self._attach_placeholder_image(
                instance=service,
                field_name="image",
                filename=f"sample_spa_service_{slugify(row['name'])}.png",
                color=row["color"],
                replace=replace_images,
            ):
                summary["Spa Services"]["images"] += 1

    def _seed_spa_packages(self, summary, replace_images):
        package_rows = [
            {
                "name": "Sample Relaxation Package",
                "description": "Sample package: massage + aromatherapy.",
                "price": Decimal("120.00"),
                "color": "#8ECAE6",
            },
            {
                "name": "Sample Glow Package",
                "description": "Sample package: facial + body scrub.",
                "price": Decimal("145.00"),
                "color": "#FFB703",
            },
            {
                "name": "Sample Couple Retreat Package",
                "description": "Sample package for two with private room setup.",
                "price": Decimal("260.00"),
                "color": "#FB8500",
            },
            {
                "name": "Sample Ultimate Renewal Package",
                "description": "Sample premium package with multiple treatments.",
                "price": Decimal("320.00"),
                "color": "#219EBC",
            },
        ]

        for row in package_rows:
            spa_package, created = SpaPackage.objects.update_or_create(
                name=row["name"],
                defaults={
                    "description": row["description"],
                    "price": row["price"],
                },
            )
            self._track(summary, "Spa Packages", created)

            if self._attach_placeholder_image(
                instance=spa_package,
                field_name="image",
                filename=f"sample_spa_package_{slugify(row['name'])}.png",
                color=row["color"],
                replace=replace_images,
            ):
                summary["Spa Packages"]["images"] += 1

    def _build_placeholder_png(self, color_hex):
        try:
            from PIL import Image

            image = Image.new("RGB", (1200, 800), color_hex)
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return self.FALLBACK_PNG

    def _attach_placeholder_image(self, instance, field_name, filename, color, replace=False):
        field_file = getattr(instance, field_name)
        if field_file and not replace:
            return False

        image_bytes = self._build_placeholder_png(color)
        field_file.save(filename, ContentFile(image_bytes), save=False)
        instance.save(update_fields=[field_name])
        return True

    def _track(self, summary, label, created):
        if created:
            summary[label]["created"] += 1
        else:
            summary[label]["updated"] += 1