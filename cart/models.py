import uuid
from django.db import models
from django.contrib.auth.models import User
from product.models import Product, ProductVariant
from store.models import Store
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class Cart(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userId_id')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, db_column='storeId_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='productId_id')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, db_column='variantId_id')
    quantity = models.PositiveIntegerField(default=1)
    selected_size = models.CharField(max_length=10, null=True, blank=True)
    selected_color = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        unique_together = ('user', 'store', 'product', 'variant')
        db_table = 'cart_cart'
        managed = True

    def __str__(self):
        variant_str = f" - {self.variant.name}" if self.variant else ""
        return f"{self.user.username}'s cart - {self.store.name} - {self.product.name}{variant_str}"

    def clean(self):
        # Validate store is active
        if not self.store.is_active:
            raise ValidationError("Cannot add products from inactive store")

        # Validate product belongs to store
        if self.product.store != self.store:
            raise ValidationError("Product does not belong to the selected store")

        # Validate variant belongs to product
        if self.variant and self.variant.product != self.product:
            raise ValidationError("Selected variant does not belong to the product")

        # Validate size if product has variants
        if self.product.has_variants:
            if not self.selected_size and self.product.available_sizes:
                raise ValidationError("Size is required for this product")
            if self.selected_size and self.selected_size not in self.product.available_sizes:
                raise ValidationError("Invalid size selected")

        # Validate color if product has variants
        if self.product.has_variants:
            if not self.selected_color and self.product.available_colors:
                raise ValidationError("Color is required for this product")
            if self.selected_color and self.selected_color not in self.product.available_colors:
                raise ValidationError("Invalid color selected")

        # Validate stock
        if self.variant:
            if self.quantity > self.variant.stock:
                raise ValidationError("Not enough stock available for selected variant")
        else:
            if self.quantity > self.product.stock:
                raise ValidationError("Not enough stock available")

    @property
    def unit_price(self):
        """Get the unit price based on product or variant"""
        if self.variant:
            return self.variant.current_price
        return self.product.base_price

    @property
    def total_price(self):
        """Calculate the total price for this cart item"""
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        """Override save to ensure quantity is at least 1 and validate the cart item"""
        if self.quantity < 1:
            self.quantity = 1
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def add_to_cart(cls, user, product, quantity=1, variant=None, size=None, color=None):
        """Helper method to add an item to cart with validation"""
        store = product.store
        
        # Check if item already exists in cart
        cart_item = cls.objects.filter(
            user=user,
            store=store,
            product=product,
            variant=variant
        ).first()

        if cart_item:
            # Update quantity if item exists
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item

        # Create new cart item
        cart_item = cls(
            user=user,
            store=store,
            product=product,
            variant=variant,
            quantity=quantity,
            selected_size=size,
            selected_color=color
        )
        cart_item.save()
        return cart_item

    def update_quantity(self, quantity):
        """Update the quantity of the cart item"""
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        self.quantity = quantity
        self.save()

    def remove(self):
        """Remove the item from cart"""
        self.delete()
