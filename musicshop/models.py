from django.contrib.contenttypes.models import ContentType
from django.db import models


class MediaType(models.Model):
    """
    Медианоситель
    """
    name = models.CharField(max_length=100, verbose_name="Название медианосителя")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Медианоситель"
        verbose_name_plural = "Медианосители"


class Member(models.Model):
    """
     Музыканты
    """
    name = models.CharField(max_length=255, verbose_name="Имя музыканта")
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Музыкант"
        verbose_name_plural = "Музыканты"


class Genre(models.Model):
    """
    Музыкальный жанр
    """
    name = models.CharField(max_length=50, verbose_name="Название жанра")
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Artist(models.Model):
    """
    Исполнитель
    """
    name = models.CharField(max_length=125, verbose_name="Исполнитель/группа")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="genre")
    members = models.ManyToManyField(Member, verbose_name="Участник", related_name="artist")
    slug = models.SlugField()

    def __str__(self):
        return f"{self.name}|{self.genre.name}"

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"


class Album(models.Model):
    """
    Альбом исполнителя
    """
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="Исполнитель")
    name = models.CharField(max_length=255, verbose_name="Название альбома")
    media_type = models.ForeignKey(MediaType, verbose_name="Носитель", on_delete=models.CASCADE)
    song_list = models.TextField(verbose_name="Трэклист")
    release_date = models.DateField(verbose_name="Дата релиза")
    descriptions = models.TextField(verbose_name="Описание", default="Описание будет позже")
    stock = models.IntegerField(default=1, verbose_name="Наличие на складе")
    price = models.DecimalField(max_digits=9, decimal_places=2)
    offer_of_the_week = models.BooleanField(default=False, verbose_name="Предложение недели")

    def __str__(self):
        return f"{self.id} | {self.artist.name} | {self.name}"

    @property
    def ct_model(self):
        return self._meta.model_name  # !!!!Метод отдает название модели!!!!

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"


class CartProduct(models.Model):
    """
    Промежуточный продукт корзины
    """
    user = models.ForeignKey("Custumer", verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey("Cart", verbose_name="Корзина", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = models.GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")

    def __str__(self):
        return f"Продукт {self.content_object.name} для коорзины"

    def save(self, *args, **kargs):
        self.final_price = self.quantity * self.content_object.price
        super().save(*args, **kargs)  # Не делаем return иначе максимум рекурсии

    class Meta:
        verbose_name = "Продукт корзины"
        verbose_name_plural = "Продукты корзины"


class Cart(models.Model):
    """
    Корзина
    """
    owner = models.ForeignKey("Custumer", verbose_name="Покупатель", on_delete=models.CASCADE)
    products = models.ManyToManyField(
        CartProduct,
        blank=True,
        null=True,
        related_name="related_cart",
        verbose_name="Продукты для корзины"
    )
    total_products = models.IntegerField(default=0, verbose_name="Общее количество товара")
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Order(models.Model):
    '''
    Заказ пользователя
    '''

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен покупателем')
    )

    BUYING_TYPE_CHOICES = (
        (BYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')

    )

    costumer = models.ForeignKey(
        'Customer',
        verbose_name="Покупатель",
        related_name='order_costumer',
        on_delete=models.CASCADE
    )  # orders
