from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_rental = models.BooleanField(default=False, help_text="True if this category is for rentals, False for food")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{'Rental' if self.is_rental else 'Food'} - {self.name}"


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = CloudinaryField('image')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_dozen = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_METHODS = (
        ('ONLINE', 'Online Payment (Paystack)'),
        ('TRANSFER', 'Bank Transfer'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('CONFIRMED', 'Confirmed & Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    order_number = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_date = models.DateTimeField()
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number} by {self.client_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_by_dozen = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class BookingQuote(models.Model):
    STATUS_CHOICES = (
        ('SUBMITTED', 'Quote Requested'),
        ('INVOICED', 'Invoice Sent'),
        ('PAID', 'Confirmed & Booked'),
    )
    SERVICE_TYPES = (
        ('DELIVERY', 'Cook & Deliver'),
        ('HOME_SERVICE', 'Cook at Client\'s House'),
        ('FULL_EVENT', 'Full Event Catering & Setup'),
    )

    quote_number = models.CharField(max_length=50, unique=True, blank=True)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50) # Wedding, Corporate, etc.
    event_date = models.DateField()
    event_address = models.TextField()
    estimated_guests = models.PositiveIntegerField()
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='DELIVERY')
    
    # Text summaries of requests sent from multi-step form JSON
    requested_menu_items = models.TextField(help_text="JSON or text summary of food items requested")
    requested_rental_items = models.TextField(help_text="JSON or text summary of rentals requested")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    generated_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quote {self.id} - {self.client_name} ({self.event_type})"


class LiveStream(models.Model):
    title = models.CharField(max_length=200)
    youtube_url = models.URLField(help_text="Link to YouTube Live or Facebook Live embed stream")
    is_live = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    client_image = CloudinaryField('image', null=True, blank=True)
    comment = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.client_name
    

class ContactInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry from {self.name} - {self.subject}"


from django.db import models

class PricingMatrixConfig(models.Model):
    standard_menu_rate = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00, help_text="Cost per head for Standard Native Tier")
    premium_menu_rate = models.DecimalField(max_digits=10, decimal_places=2, default=4500.00, help_text="Cost per head for Premium Continental Buffet")
    executive_menu_rate = models.DecimalField(max_digits=10, decimal_places=2, default=7500.00, help_text="Cost per head for Executive Imperial Banquet")
    canopy_base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=15000.00, help_text="Cost charged per chunk of 50 guests if checked")

    class Meta:
        verbose_name = "Pricing Matrix Configuration"
        verbose_name_plural = "Pricing Matrix Configurations"

    def __str__(self):
        return "Global Pricing Matrix Constants Profile"

    def save(self, *args, **kwargs):
        # Enforces a singleton structure: overrides save to ensure only one record exists
        self.pk = 1
        super(PricingMatrixConfig, self).save(*args, **kwargs)



class HeroSlide(models.Model):
    title = models.CharField(max_length=150, blank=True, help_text="For internal tracking reference.")
    
    # 🟢 CLOUDINARY UPDATE: Uses CloudinaryField and assigns a secure remote storage folder path
    image = CloudinaryField('image', folder='hero_carousel', help_text="Upload high-res banner photos straight to Cloudinary.")
    
    alt_text = models.CharField(max_length=200, default="Dina Catering & Luxury Rentals Setup")
    order = models.PositiveIntegerField(default=0, help_text="Set display hierarchy position sequence.")
    is_active = models.BooleanField(default=True, help_text="Toggle visibility without deleting.")

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f"Hero Slide Banner #{self.id}"