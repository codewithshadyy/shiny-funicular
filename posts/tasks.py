import io
from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image


@shared_task(bind=True,max_retries=3)
def process_media(self, media_id):
    
    from .models import Media
    
    try:
        media = Media.objects.get(id=media_id)
        media.processing_status = "processing"
        media.save(update_fields=["processing_status"])

        if media.media_type == "image":
            _process_image(media)
        elif media.media_type == "video":
            _process_video(media)

        media.processing_status = "ready"
        media.save(update_fields=["processing_status"])

    except Exception as exc:
        media.processing_status = "failed"
        media.save(update_fields=["processing_status"])
        raise self.retry(exc=exc, countdown=10)
    

def _process_image(media):
    with default_storage.open(media.storage_key, "rb") as f:
        image = Image.open(f)
        media.width, media.height = image.size
        media.save(update_fields=["width", "height"])
        
def _process_video(media):
    import time
    time.sleep(3)  
    media.duration_seconds = 42  
    media.save(update_fields=["duration_seconds"])            