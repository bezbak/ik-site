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
        ("Страница «О компании» (/about-us.html) — видео слева", {
            "fields": ("about_us_video", "about_us_video_preview"),
        }),
        ("Страница «О компании» (/about-us.html) — фото справа", {
            "fields": ("about_us_photo", "about_us_photo_preview"),
        }),
    )
    readonly_fields = (
        "apartments_hero_preview", "cottages_hero_preview",
        "about_us_video_preview", "about_us_photo_preview",
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

    def about_us_photo_preview(self, obj):
        return self._preview(obj.about_us_photo)

    about_us_photo_preview.short_description = "Превью"

    def about_us_video_preview(self, obj):
        if obj.about_us_video:
            return format_html(
                '<video src="{}" muted loop autoplay playsinline style="max-height:160px;border-radius:8px"></video>',
                obj.about_us_video.url,
            )
        return "—"

    about_us_video_preview.short_description = "Превью"

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


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
