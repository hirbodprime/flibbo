from django.db.models.signals import post_save,pre_save,m2m_changed
from django.dispatch import receiver
from posts.models import ReportPost, TweetPostModel, TweetCommentModel
@receiver(post_save, sender=TweetPostModel)
def create_share_link(sender, created, instance, **kwargs):
    if created:
        from firebase_dynamic_links import dynamic_link_builder
        builder = dynamic_link_builder(api_key='AIzaSyBq77V9pbQXFDoM-eOK5G67NB6GxvXXBcc')
        options = {
            'link': f'https://flibbo.com/share?post={instance.id}',
            'apn': 'com.flibbo.app', 
            'ibi': 'com.flibbo.app'
        }
        try:
            short_link = builder.generate_short_link(app_code='flibbo', **options)
            instance.share_post = short_link
            instance.save()
        except Exception as e:
            print(str(e))
@receiver(m2m_changed, sender=TweetCommentModel.reported_by.through)
def delete_comment_on_100_reports(sender, instance, **kwargs):
    if instance.reported_by.count() >= 100:
        instance.delete()

@receiver(post_save, sender='posts.ReportPost')  # Replace 'your_app_name' with the name of your Django app
def delete_post_if_reports_exceed_threshold(sender, instance, **kwargs):
    if instance.report_count >= 200:
        post_to_delete = TweetPostModel.objects.get(id=instance.post.id)  # Keep a reference to the post instance\
        post_to_delete.hide = True
        post_to_delete.save()