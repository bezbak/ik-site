from django.contrib import admin
from django.utils.html import format_html

from .models import Document, FAQItem, Property, PropertyImage, SiteSettings


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
    list_display = ("title", "property_type", "area_sqm", "room_line", "plan_preview", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("property_type", "is_published")
    search_fields = ("slug", "description")
    prepopulated_fields = {"slug": ()}
    inlines = [PropertyImageInline]
    fieldsets = (
        (None, {"fields": ("property_type", "slug", "area_sqm", "bedrooms", "bathrooms", "room_summary")}),
        ("Планировка и описание", {"fields": ("floor_plan_image", "description")}),
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
    list_display = ("phone_number", "whatsapp_number")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
