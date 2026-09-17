import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Document, FAQItem, Lead, Property


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
    """Unified catalog page: all published properties (apartments + cottages),
    with an optional `?type=` query param used to pre-select the client-side filter tab.
    """
    active_type = request.GET.get("type", "")
    if active_type not in (Property.APARTMENT, Property.COTTAGE):
        active_type = ""

    properties_qs = Property.objects.filter(is_published=True)
    faq_items = FAQItem.objects.filter(is_published=True)
    documents = Document.objects.filter(is_published=True)
    context = {
        "active_type": active_type,
        "properties": properties_qs,
        "documents": documents,
        "faq_items": faq_items,
        **_common_context(properties_qs, faq_items, documents),
    }
    return render(request, "properties.html", context)


def properties_redirect(request, property_type):
    """Old /cottages/ and /apartments/ URLs now point at the unified catalog page."""
    url = reverse("catalog:properties")
    return redirect(f"{url}?type={property_type}", permanent=True)


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
