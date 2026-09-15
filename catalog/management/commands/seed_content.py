from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from catalog.models import Document, FAQItem, Property, SiteSettings

PUBLIC = Path(settings.BASE_DIR) / "public"


def attach_image(field, source_path, name=None):
    source_path = Path(source_path)
    if not source_path.exists():
        return
    with open(source_path, "rb") as fh:
        field.save(name or source_path.name, File(fh), save=False)


class Command(BaseCommand):
    help = "Seed the database with AVAT 365's current live content (properties, documents, FAQ)."

    def handle(self, *args, **options):
        SiteSettings.load()

        properties = [
            dict(property_type="apartment", slug="apartment-45-87", area_sqm="45.87",
                 bedrooms=1, bathrooms=1, room_summary="кухня-гостиная",
                 image="img/plan-apt-45.jpg",
                 description="Своё пространство для поездок на Иссык-Куль. Отдельная спальня и кухня-гостиная в пятиэтажном апарт-отеле, рядом со всей инфраструктурой курорта.",
                 order=1),
            dict(property_type="apartment", slug="apartment-93-45", area_sqm="93.45",
                 bedrooms=2, bathrooms=2, room_summary="",
                 image="img/plan-apt-93.jpg",
                 description="Просторные апартаменты для семьи или инвестиций: две спальни, два санузла и кухня-гостиная в пятиэтажном апарт-отеле AVAT 365.",
                 order=2),
            dict(property_type="cottage", slug="cottage-77-22", area_sqm="77.22",
                 bedrooms=2, bathrooms=2, room_summary="",
                 image="img/plan-cottage-77.png",
                 description="Одноэтажный частный коттедж с собственным участком. Две спальни, два санузла — компактный формат для отдыха и жизни у озера.",
                 order=1),
            dict(property_type="cottage", slug="cottage-110-89", area_sqm="110.89",
                 bedrooms=3, bathrooms=2, room_summary="",
                 image="img/plan-cottage-110.png",
                 description="Просторный коттедж на три спальни с двумя санузлами — для семейного отдыха на Иссык-Куле круглый год.",
                 order=2),
            dict(property_type="cottage", slug="cottage-144-89", area_sqm="144.89",
                 bedrooms=3, bathrooms=2, room_summary="",
                 image="img/plan-cottage-145.jpg",
                 description="Самый большой формат коттеджа AVAT 365: три спальни, два санузла и максимум пространства для большой семьи.",
                 order=3),
        ]

        for data in properties:
            image_path = PUBLIC / data.pop("image")
            obj, created = Property.objects.update_or_create(
                slug=data["slug"], defaults=data,
            )
            if not obj.floor_plan_image:
                attach_image(obj.floor_plan_image, image_path)
                obj.save()
            self.stdout.write(f"{'Created' if created else 'Updated'} property: {obj}")

        documents = [
            dict(title="Презентация проекта", order=1,
                 description="Концепция, генплан и инфраструктура AVAT 365 в одной презентации.",
                 file="public/documents/AVAT-365-presentation.pdf"),
            dict(title="Брендбук AVAT 365", order=2,
                 description="Логотип, цвета и визуальный стиль проекта для партнёров и СМИ.",
                 file="public/documents/Avat_brandbook.pdf"),
            dict(title="Разрешительная документация", order=3,
                 description="Полный пакет документов на проект доступен для ознакомления в отделе продаж.",
                 file=None),
        ]
        for data in documents:
            file_path = data.pop("file")
            obj, created = Document.objects.update_or_create(title=data["title"], defaults=data)
            if file_path and not obj.file:
                attach_image(obj.file, Path(settings.BASE_DIR) / file_path)
                obj.save()
            self.stdout.write(f"{'Created' if created else 'Updated'} document: {obj}")

        faqs = [
            ("Какие апартаменты доступны?",
             "В проектных материалах представлены апартаменты площадью 45,87 м² и 93,45 м². Для уточнения напишите пожалуйста в отдел продаж."),
            ("Что входит в стоимость?",
             "Ваш коттедж или апартаменты, а также вся инфраструктура 365 дней в году."),
            ("Какой первоначальный взнос?",
             "Первоначальный взнос 30%. Далее беспроцентная рассрочка на оставшийся период строительства."),
            ("Есть ли рассрочка?",
             "Да. Мы предоставляем возможность беспроцентной рассрочки на 24 месяца."),
            ("Когда планируется завершение строительства?",
             "Завершение строительства планируется на 4-й квартал 2028 года."),
            ("Как будет организован доступ к инфраструктуре?",
             "Все жители будут иметь доступ ко всей инфраструктуре комплекса вне зависимости от выбранного типа жилья."),
            ("Как посмотреть объект и документы?",
             "Приглашаем вас в офис для ознакомления со всеми документами и проектом."),
        ]
        for i, (question, answer) in enumerate(faqs, start=1):
            obj, created = FAQItem.objects.update_or_create(
                question=question, defaults={"answer": answer, "order": i},
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} FAQ: {obj}")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
