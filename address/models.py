import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.

class ShippingAddress(models.Model):

    class AddressType(models.TextChoices):
        HOME = 'home', _('Home')
        OFFICE = 'office', _('Office')
        SCHOOL = 'school', _('School')
        MARKET = 'market', _('Market')
        OTHER = 'other', _('Other')
        BUSINESS = 'business', _('Business')
        MAILING = 'mailing', _('Mailing')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    # User relationship
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shipping_addresses',
        help_text="The user this shipping address belongs to"
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Latitude'),
        help_text=_('Geographical latitude of the address')
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Longitude'),
        help_text=_('Geographical longitude of the address')
    )

    # Address details
   
    address = models.CharField(
        max_length=255,
        verbose_name=_('Address'),
        help_text=_('Full address including street, city, state, and postal code')
    )

    city = models.CharField(
        max_length=255,
        verbose_name=_('City'),
        help_text=_('City name')
    )
    state = models.CharField(
        max_length=255,
        verbose_name=_('State'),
        help_text="State, province, or region"
    )
    country = models.CharField(
       max_length=100,
        verbose_name=_('Country'),
        help_text="Country"
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_('Postal Code'),
        help_text=_('Postal or ZIP code'),
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\s\-]+$',
                message=_('Enter a valid postal code')
            )
        ]
    )
    phone = models.CharField(
       max_length=100,
        verbose_name=_('Phone'),
        help_text="Phone",
        blank=False,
        null=False
    )
    additional_phone = models.CharField(
       max_length=100,
        verbose_name=_('Additional phone '),
        help_text="Additional phone",
        blank=True,
        null=True
    )

    # Address status
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('Default Address'),
        help_text=_('Whether this is the user\'s default address')
    )

    # Address type
    address_type = models.CharField(
        max_length=10,
        choices=AddressType.choices,
        default=AddressType.HOME,
        verbose_name=_('Address Type'),
        help_text=_('Type of address (home, office, etc.)')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this address was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this address was last updated"
    )

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['user', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            )
        ]

    def __str__(self):
        """Return a string representation of the address"""
        try:
            parts = []
            
            if self.address:
                parts.append(str(self.address))
            if self.city:
                parts.append(str(self.city))
            if self.state:
                parts.append(str(self.state))
            if self.country:
                parts.append(str(self.country))
                
            return ", ".join(parts) if parts else f"Shipping Address {self.id}"
        except Exception:
            return f"Shipping Address {self.id}"

    def clean(self):
        """Validate the model instance."""
        super().clean()
        
        # Ensure required fields are not empty
        if not self.address or not self.address.strip():
            raise ValidationError({'address': 'Address is required.'})
        
        if not self.city or not self.city.strip():
            raise ValidationError({'city': 'City is required.'})
            
        if not self.phone or not self.phone.strip():
            raise ValidationError({'phone': 'Phone number is required.'})

    def save(self, *args, **kwargs):
        """Override save to handle default address logic"""
        # If this is the user's first address, make it default
        if not self.pk and not ShippingAddress.objects.filter(user=self.user).exists():
            self.is_default = True
        # Ensure only one default per user
        if self.is_default:
            ShippingAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def coordinates(self):
        """Return coordinates as a dictionary"""
        if self.latitude and self.longitude:
            return {
                'latitude': self.latitude,
                'longitude': self.longitude
            }
        return None

    @property
    def full_address(self):
        """Return the complete formatted address"""
        try:
            parts = []
            
            if self.address:
                parts.append(str(self.address))
            if self.city:
                parts.append(str(self.city))
            if self.state:
                parts.append(str(self.state))
            if self.postal_code:
                parts.append(str(self.postal_code))
            if self.country:
                parts.append(str(self.country))
            
            address_str = ", ".join(parts) if parts else "No address provided"
            
            # Add coordinates if available
            if self.latitude and self.longitude:
                address_str += f" (Lat: {self.latitude:.6f}, Lng: {self.longitude:.6f})"
                
            return address_str
        except Exception:
            return f"Shipping Address {self.id}"

    def soft_delete(self, user=None):
        pass

    def restore(self, user=None):
        pass

    