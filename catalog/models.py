from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class SiteSettings(models.Model):
    """Singleton-style row holding contact details reused across templates."""

    phone_number = models.CharField(
        max_length=32, default="+996222170399",
        help_text="Формат: +996222170399 (используется для ссылок tel:)",
    )
    whatsapp_number = models.CharField(
        max_length=32, default="996222170399",
        help_text="Только цифры, без + и пробелов (используется для ссылок wa.me)",
    )
    address = models.CharField(
        max_length=200, blank=True, default="Токтогула 147, кабинет 40",
        verbose_name="Адрес офиса",
    )

    class Meta:
        verbose_name = "Контакты сайта"
        verbose_name_plural = "Контакты сайта"

    def __str__(self):
        return "Контакты сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Property(models.Model):
    APARTMENT = "apartment"
    COTTAGE = "cottage"
    TYPE_CHOICES = [
        (APARTMENT, "Апартаменты"),
        (COTTAGE, "Коттедж"),
    ]

    property_type = models.CharField(max_length=16, choices=TYPE_CHOICES, verbose_name="Тип")
    slug = models.SlugField(max_length=80, unique=True, help_text="Используется в адресе страницы, например cottage-77")
    area_sqm = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Площадь, м²")
    bedrooms = models.PositiveSmallIntegerField(verbose_name="Спален")
    bathrooms = models.PositiveSmallIntegerField(verbose_name="Санузлов")
    room_summary = models.CharField(
        max_length=120, blank=True,
        help_text="Например «кухня-гостиная» — если пусто, будет показано «N спальни · N санузла»",
    )
    floor_plan_image = models.ImageField(upload_to="properties/plans/", verbose_name="Изображение планировки")
    description = models.TextField(blank=True, verbose_name="Описание для детальной страницы")
    price = models.CharField(
        max_length=60, blank=True, verbose_name="Цена",
        help_text="Например «от $45 000» или «По запросу» — если пусто, цена не показывается",
    )
    location = models.CharField(
        max_length=200, blank=True, verbose_name="Адрес/локация",
        default="Кыргызстан, Иссык-Куль, с. Чон-Сары-Ой",
    )
    amenities = models.CharField(
        max_length=300, blank=True, verbose_name="Удобства",
        help_text="Через запятую, например: Терраса, Парковка, Кладовая",
    )
    video = models.FileField(
        upload_to="properties/video/", blank=True, null=True, verbose_name="Видео (mp4)",
        help_text="Необязательно — короткий видео-обзор для галереи на детальной странице",
    )
    whatsapp_message = models.CharField(
        max_length=300, blank=True,
        help_text="Если пусто — сформируется автоматически из типа и площади",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок показа")
    is_published = models.BooleanField(default=True, verbose_name="Показывать на сайте")

    class Meta:
        verbose_name = "Планировка"
        verbose_name_plural = "Планировки"
        ordering = ["property_type", "order", "area_sqm"]

    def __str__(self):
        return self.title

    @property
    def title(self):
        label = self.get_property_type_display()
        area = f"{float(self.area_sqm):g}".replace(".", ",")
        return f"{label} {area} м²"

    @property
    def room_line(self):
        if self.room_summary:
            return self.room_summary
        beds = "спальня" if self.bedrooms == 1 else "спальни" if self.bedrooms in (2, 3, 4) else "спален"
        baths = "санузел" if self.bathrooms == 1 else "санузла" if self.bathrooms in (2, 3, 4) else "санузлов"
        return f"{self.bedrooms} {beds} · {self.bathrooms} {baths}"

    def whatsapp_text(self):
        return self.whatsapp_message or f"Здравствуйте! Интересует {self.title} в AVAT 365."

    def get_absolute_url(self):
        return reverse("catalog:property_detail", kwargs={"slug": self.slug})

    @property
    def amenities_list(self):
        return [a.strip() for a in self.amenities.split(",") if a.strip()]


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name="gallery_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="properties/gallery/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Фото планировки"
        verbose_name_plural = "Фото планировки (галерея)"
        ordering = ["order"]

    def __str__(self):
        return f"Фото для {self.property}"


class Document(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название")
    description = models.CharField(max_length=300, blank=True, verbose_name="Описание")
    file = models.FileField(
        upload_to="documents/", blank=True, null=True, verbose_name="Файл (PDF)",
        help_text="Если файл не загружен — вместо «Смотреть/Скачать» покажется кнопка «Запросить документы» (WhatsApp)",
    )
    size_label = models.CharField(
        max_length=30, blank=True, verbose_name="Подпись размера",
        help_text="Например «PDF · 8 МБ». Если пусто — посчитается автоматически по загруженному файлу.",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок показа")
    is_published = models.BooleanField(default=True, verbose_name="Показывать на сайте")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы проекта"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    @property
    def display_size(self):
        if self.size_label:
            return self.size_label
        if self.file:
            try:
                mb = self.file.size / (1024 * 1024)
                return f"PDF · {mb:.0f} МБ" if mb >= 1 else f"PDF · {self.file.size // 1024} КБ"
            except (OSError, ValueError):
                return ""
        return ""


class Lead(models.Model):
    """A contact-form submission from the site's lead-capture CTAs."""

    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    phone = models.CharField(max_length=32, verbose_name="Телефон (WhatsApp)")
    property_type = models.CharField(
        max_length=16, choices=Property.TYPE_CHOICES, verbose_name="Интересует",
    )
    source_page = models.CharField(
        max_length=200, blank=True, verbose_name="Источник",
        help_text="Страница, с которой отправлена заявка",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    is_processed = models.BooleanField(default=False, verbose_name="Обработана")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.phone}"


class FAQItem(models.Model):
    question = models.CharField(max_length=200, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок показа")
    is_published = models.BooleanField(default=True, verbose_name="Показывать на сайте")

    class Meta:
        verbose_name = "Вопрос FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question
