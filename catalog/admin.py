from django.contrib import admin
from django.utils.html import format_html

from .models import Document, FAQItem, Lead, Property, PropertyImage, SiteSettings


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "preview", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px">', obj.image.url)
        return "—"

    preview.short_description = "Превью"


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title", "property_type", "area_sqm", "room_line", "price", "plan_preview", "order", "is_published",
    )
    list_editable = ("price", "order", "is_published")
    list_filter = ("property_type", "is_published")
    search_fields = ("slug", "description", "location", "amenities")
    prepopulated_fields = {"slug": ()}
    inlines = [PropertyImageInline]
    fieldsets = (
        (None, {"fields": ("property_type", "slug", "area_sqm", "bedrooms", "bathrooms", "room_summary")}),
        ("Планировка и описание", {"fields": ("floor_plan_image", "description")}),
        ("Витрина (цена, локация, удобства, видео)", {"fields": ("price", "location", "amenities", "video")}),
        ("WhatsApp", {"fields": ("whatsapp_message",)}),
        ("Показ на сайте", {"fields": ("order", "is_published")}),
    )

    def plan_preview(self, obj):
        if obj.floor_plan_image:
            return format_html('<img src="{}" style="height:50px;border-radius:6px">', obj.floor_plan_image.url)
        return "—"

    plan_preview.short_description = "Планировка"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "display_size", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_published")
    list_editable = ("order", "is_published")


# Every photo/video slot on the About Us page, in the order they appear on
# the page (numbered in their verbose_name too, so the admin list and the
# page match up without needing to guess which is which).
_ABOUT_US_IMAGE_FIELDS = (
    "about_us_photo", "about_us_experience_photo", "about_us_trust_photo",
    "about_us_ticker_photo_1", "about_us_ticker_photo_2", "about_us_ticker_photo_3",
    "about_us_ticker_photo_4", "about_us_ticker_photo_5",
)
_ABOUT_US_VIDEO_FIELDS = ("about_us_video", "about_us_mission_video")


def _make_image_preview(field_name):
    def preview(self, obj):
        image = getattr(obj, field_name)
        if image:
            return format_html('<img src="{}" style="max-height:160px;border-radius:8px">', image.url)
        return "—"

    preview.short_description = "Превью"
    return preview


def _make_video_preview(field_name):
    def preview(self, obj):
        video = getattr(obj, field_name)
        if video:
            return format_html(
                '<video src="{}" muted loop autoplay playsinline style="max-height:160px;border-radius:8px"></video>',
                video.url,
            )
        return "—"

    preview.short_description = "Превью"
    return preview


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "whatsapp_number", "address")
    fieldsets = (
        ("Контакты", {"fields": ("phone_number", "whatsapp_number", "address")}),
        ("Страница «Апартаменты» (/apartments/)", {
            "fields": ("apartments_hero_image", "apartments_hero_preview"),
        }),
        ("Страница «Коттеджи» (/cottages/)", {
            "fields": ("cottages_hero_image", "cottages_hero_preview"),
        }),
        ("Страница «О компании» (/about-us.html) — все фото и видео", {
            "description": "Каждое поле подписано номером и местом на странице, в порядке сверху вниз.",
            "fields": (
                "about_us_video", "about_us_video_preview",
                "about_us_photo", "about_us_photo_preview",
                "about_us_mission_video", "about_us_mission_video_preview",
                "about_us_experience_photo", "about_us_experience_photo_preview",
                "about_us_trust_photo", "about_us_trust_photo_preview",
                "about_us_ticker_photo_1", "about_us_ticker_photo_1_preview",
                "about_us_ticker_photo_2", "about_us_ticker_photo_2_preview",
                "about_us_ticker_photo_3", "about_us_ticker_photo_3_preview",
                "about_us_ticker_photo_4", "about_us_ticker_photo_4_preview",
                "about_us_ticker_photo_5", "about_us_ticker_photo_5_preview",
            ),
        }),
    )
    readonly_fields = (
        "apartments_hero_preview", "cottages_hero_preview",
        *(f"{name}_preview" for name in _ABOUT_US_IMAGE_FIELDS),
        *(f"{name}_preview" for name in _ABOUT_US_VIDEO_FIELDS),
    )

    def _preview(self, image):
        if image:
            return format_html('<img src="{}" style="max-height:160px;border-radius:8px">', image.url)
        return "—"

    def apartments_hero_preview(self, obj):
        return self._preview(obj.apartments_hero_image)

    apartments_hero_preview.short_description = "Превью"

    def cottages_hero_preview(self, obj):
        return self._preview(obj.cottages_hero_image)

    cottages_hero_preview.short_description = "Превью"

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


for _field_name in _ABOUT_US_IMAGE_FIELDS:
    setattr(SiteSettingsAdmin, f"{_field_name}_preview", _make_image_preview(_field_name))
for _field_name in _ABOUT_US_VIDEO_FIELDS:
    setattr(SiteSettingsAdmin, f"{_field_name}_preview", _make_video_preview(_field_name))


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "property_type", "source_page", "created_at", "is_processed")
    list_editable = ("is_processed",)
    list_filter = ("property_type", "is_processed", "created_at")
    search_fields = ("full_name", "phone")
    readonly_fields = ("full_name", "phone", "property_type", "source_page", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False
