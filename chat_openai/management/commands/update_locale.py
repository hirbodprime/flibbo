from django.core.management.base import BaseCommand
from chat_openai.models import VoiceActorModel

class Command(BaseCommand):
    help = 'Updates the locale to "zh" for all VoiceActorModel instances with Chinese language'

    def handle(self, *args, **kwargs):
        # Filtering VoiceActorModel instances where language is Chinese
        voice_actors = VoiceActorModel.objects.filter(language__icontains='Chinese')

        for actor in voice_actors:
            actor.locale = 'zh'
            actor.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {voice_actors.count()} voice actors'))
