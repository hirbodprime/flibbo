from django.core.management.base import BaseCommand
import json
from chat_openai.models import VoiceActorModel  # Replace 'yourapp' with your actual app name
class Command(BaseCommand):
    help = 'Load or update a list of voice actors from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The JSON file path')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path, 'r') as file:
            voice_actors = json.load(file)

            for actor in voice_actors:
                # Extract country from the language field
                country = actor['language'].split('(')[-1].rstrip(')')

                # Check if the actor already exists
                obj, created = VoiceActorModel.objects.update_or_create(
                    voice_id=actor['id'],
                    defaults={
                        'name': actor['name'],
                        'gender': actor['gender'],
                        'locale': actor['locale'],
                        'language': actor['language'],
                        'access': actor['access'],
                        'provider': actor['provider'],
                        'country': country
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new voice actor: {obj.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated existing voice actor: {obj.name}'))
