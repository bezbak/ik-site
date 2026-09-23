import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Document, FAQItem, Lead, Property, SiteSettings


def _serialize_properties(qs):
    return [
        {
            "title": p.title,
            "property_type": p.property_type,
            "room_line": p.room_line,
            "bedrooms": p.bedrooms,
            "bathrooms": p.bathrooms,
            "area_sqm": str(p.area_sqm),
            "price": p.price,
            "location": p.location,
            "image": p.floor_plan_image.url if p.floor_plan_image else "",
            "url": p.get_absolute_url(),
        }
        for p in qs
    ]


def _serialize_faq(qs):
    return [{"question": f.question, "answer": f.answer} for f in qs]


def _serialize_documents(qs):
    return [
        {
            "title": d.title,
            "description": d.description,
            "size_label": d.display_size,
            "file": d.file.url if d.file else "",
        }
        for d in qs
    ]


def _common_context(properties, faq_items, documents):
    return {
        "properties_json": json.dumps(_serialize_properties(properties), cls=DjangoJSONEncoder),
        "faq_json": json.dumps(_serialize_faq(faq_items), cls=DjangoJSONEncoder),
        "documents_json": json.dumps(_serialize_documents(documents), cls=DjangoJSONEncoder),
    }


def _custom_main_html_json(request, template_name, context):
    """Render a page's custom "main content" fragment to a JSON-encoded string.

    The shared page shell (nav/footer/etc, inherited from the Framer export)
    hydrates via a bundled React app that recreates its own original content
    on top of anything structurally different, wiping plain server-rendered
    HTML placed inside its root. Storing the fragment as a JS string constant
    instead (safe from any DOM manipulation) lets the page's patch() loop
    re-insert it after every hydration pass, no matter how many times the
    DOM around it gets rebuilt.
    """
    html = render_to_string(template_name, context, request=request)
    return json.dumps(html)


def home(request):
    properties = Property.objects.filter(is_published=True)
    faq_items = FAQItem.objects.filter(is_published=True)
    documents = Document.objects.filter(is_published=True)
    context = {
        "properties": properties,
        "documents": documents,
        "faq_items": faq_items,
        **_common_context(properties, faq_items, documents),
    }
    return render(request, "home.html", context)


def properties(request):
    """Dedicated catalog page: all published properties (apartments + cottages),
    with an optional `?type=` query param used to pre-select the filter tab.

    Unlike home, this page's content isn't part of the shared one-page design
    (no hero/about/infrastructure/etc.), so it reuses the property_detail/contact_us
    technique: render a standalone fragment and let the page's patch() loop swap
    it in for the whole body, instead of relying on the shared plans section.
    """
    active_type = request.GET.get("type", "")
    if active_type not in (Property.APARTMENT, Property.COTTAGE):
        active_type = ""

    properties_qs = Property.objects.filter(is_published=True)
    bedroom_options = sorted(set(properties_qs.values_list("bedrooms", flat=True)))
    content_context = {
        "properties": properties_qs,
        "active_type": active_type,
        "bedroom_options": bedroom_options,
    }
    # The page reuses the shared footer/head-scripts block, which references
    # PROPERTIES_DATA/FAQ_DATA/DOCUMENTS_DATA as inline JS — keep those defined
    # (even if empty) so that script block doesn't fail to parse.
    return render(request, "properties.html", {
        "active_type": active_type,
        "custom_main_html_json": _custom_main_html_json(
            request, "_properties_content.html", content_context,
        ),
        "properties_json": "[]", "faq_json": "[]", "documents_json": "[]",
    })


# SEO copy per type for the dedicated /apartments/ and /cottages/ landing
# pages — each is a full copy of the home page (not a filtered view of
# /properties/) so ad campaigns can target and report on them separately.
# The hero headline/description swap itself is done client-side in home.html
# (see TYPE_HERO_COPY there) since Framer's hydration can revert server-side
# text changes back to whatever's baked into its compiled bundle.
_TYPE_LANDING_SEO = {
    Property.APARTMENT: {
        "page_title": "Апартаменты AVAT 365 — планировки и цены",
        "page_description": "Апартаменты AVAT 365 на Иссык-Куле: отдельные спальни и кухни-гостиные в разных планировочных решениях. Площади, цены и фото планировок.",
        "canonical_path": "/apartments/",
        "og_url": "https://avatconstruction.com/apartments/",
    },
    Property.COTTAGE: {
        "page_title": "Коттеджи AVAT 365 — планировки и цены",
        "page_description": "Коттеджи AVAT 365 на Иссык-Куле: одноэтажные дома трёх типов площадью 78, 110 и 145 м². Планировки, цены и фото.",
        "canonical_path": "/cottages/",
        "og_url": "https://avatconstruction.com/cottages/",
    },
}


def _type_landing_page(request, property_type):
    """Dedicated /apartments/ or /cottages/ page: the exact same one-page
    home layout (hero, about, infrastructure, services, location, FAQ,
    footer...), with only the hero copy and the "Планировки" plans grid
    locked to one property type, so each page can run as its own,
    separately trackable ad landing page.
    """
    seo = _TYPE_LANDING_SEO[property_type]
    properties_qs = Property.objects.filter(is_published=True, property_type=property_type)
    faq_items = FAQItem.objects.filter(is_published=True)
    documents = Document.objects.filter(is_published=True)
    site_settings = SiteSettings.load()
    hero_image = (
        site_settings.apartments_hero_image
        if property_type == Property.APARTMENT
        else site_settings.cottages_hero_image
    )
    context = {
        "properties": properties_qs,
        "documents": documents,
        "faq_items": faq_items,
        "property_type": property_type,
        "page_title": seo["page_title"],
        "page_description": seo["page_description"],
        "canonical_path": seo["canonical_path"],
        "og_url": seo["og_url"],
        "hero_bg_image": hero_image.url if hero_image else "",
        **_common_context(properties_qs, faq_items, documents),
    }
    return render(request, "home.html", context)


def apartments(request):
    return _type_landing_page(request, Property.APARTMENT)


def cottages(request):
    return _type_landing_page(request, Property.COTTAGE)


def property_detail(request, slug):
    prop = get_object_or_404(
        Property.objects.prefetch_related("gallery_images"), slug=slug, is_published=True,
    )
    related = (
        Property.objects.filter(is_published=True, property_type=prop.property_type)
        .exclude(pk=prop.pk)[:3]
    )
    content_context = {"property": prop, "related_properties": related}
    # The page reuses the shared footer/head-scripts block, which references
    # PROPERTIES_DATA/FAQ_DATA/DOCUMENTS_DATA as inline JS — keep those defined
    # (even if empty) so that script block doesn't fail to parse.
    return render(request, "property_detail.html", {
        "property": prop,
        "related_properties": related,
        "custom_main_html_json": _custom_main_html_json(
            request, "_property_detail_content.html", content_context,
        ),
        "properties_json": "[]", "faq_json": "[]", "documents_json": "[]",
    })


def contact_us(request):
    # The page reuses the shared footer/head-scripts block, which references
    # PROPERTIES_DATA/FAQ_DATA/DOCUMENTS_DATA as inline JS — keep those defined
    # (even if empty) so that script block doesn't fail to parse.
    return render(request, "contact_us.html", {
        "custom_main_html_json": _custom_main_html_json(request, "_contact_us_content.html", {}),
        "properties_json": "[]", "faq_json": "[]", "documents_json": "[]",
    })


def about_us(request):
    site_settings = SiteSettings.load()
    media_fields = [
        "about_us_video", "about_us_photo", "about_us_mission_video",
        "about_us_experience_photo", "about_us_trust_photo",
        "about_us_ticker_photo_1", "about_us_ticker_photo_2", "about_us_ticker_photo_3",
        "about_us_ticker_photo_4", "about_us_ticker_photo_5",
    ]
    context = {
        f"{name}_url": (getattr(site_settings, name).url if getattr(site_settings, name) else "")
        for name in media_fields
    }
    return render(request, "about_us.html", context)


@csrf_exempt
@require_POST
def lead_create(request):
    # Honeypot: real visitors never fill this hidden field, bots often do.
    if request.POST.get("website"):
        return JsonResponse({"ok": True})

    full_name = (request.POST.get("full_name") or "").strip()[:150]
    phone = (request.POST.get("phone") or "").strip()[:32]
    property_type = request.POST.get("property_type") or ""
    source_page = (request.POST.get("source_page") or "").strip()[:200]

    if not full_name or not phone or property_type not in (Property.APARTMENT, Property.COTTAGE):
        return JsonResponse({"ok": False, "error": "invalid"}, status=400)

    Lead.objects.create(
        full_name=full_name, phone=phone, property_type=property_type, source_page=source_page,
    )
    return JsonResponse({"ok": True})
