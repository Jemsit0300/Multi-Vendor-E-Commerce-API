from django.db import models

class Vendor(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='vendor_profile')
    store_name = models.CharField(max_length=255)
    store_description = models.TextField(blank=True, null=True)
    store_logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name