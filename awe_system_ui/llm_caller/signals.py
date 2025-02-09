from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import BatchProcessing


@receiver(pre_delete, sender=BatchProcessing)
def stop_batch_on_delete(sender, instance, **kwargs):
    """Stop batch processing when the batch is deleted."""
    instance.stop_processing()
