import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render

from .models import Document, FAQItem, Property


def _serialize_properties(qs):
    return [
        {
            "title": p.title,
            "room_line": p.room_line,
            "bedrooms": p.bedrooms,
            "bathrooms": p.bathrooms,
            "area_sqm": str(p.area_sqm),
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


def property_list(request, property_type):
    properties = Property.objects.filter(is_published=True, property_type=property_type)
    faq_items = FAQItem.objects.filter(is_published=True)
    documents = Document.objects.filter(is_published=True)
    context = {
        "property_type": property_type,
        "properties": properties,
        "documents": documents,
        "faq_items": faq_items,
        **_common_context(properties, faq_items, documents),
    }
    return render(request, "property_list.html", context)


def property_detail(request, slug):
    prop = get_object_or_404(Property, slug=slug, is_published=True)
    return render(request, "property_detail.html", {"property": prop})
