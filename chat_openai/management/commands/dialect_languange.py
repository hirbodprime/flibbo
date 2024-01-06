from django.core.management.base import BaseCommand
import json
from chat_openai.models import Language,Dialect

class Command(BaseCommand):
    help = 'Load or update a list of voice actors from a JSON file'
    def handle(self, *args, **kwargs):
        with open('chat_openai/dialect.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data['data']:
            full_name = item['name']

            # Extract the first two letters of the name
            initials = full_name[:2]

            # Extract the part of the name after the first space
            name_post_space = full_name.split(' ', 1)[1] if ' ' in full_name else ''

            dialect, created = Dialect.objects.get_or_create(
                _id=item['_id'],
                defaults={
                    'name': full_name, 
                    'name_post_space': name_post_space,
                    'initials': initials
                }
            )

            if created:
                print(f'Added new dialect: {dialect.name}')
            else:
                print(f'Dialect already exists: {dialect.name}')
        # for name in Dialect.objects.all():
        # # find_country_data(name.name_post_space)
        # # print(name)
        #     country = pycountry.countries.get(name=name.name_post_space)
        #     if country:
        #         print(country.alpha_2)
        #         name.initials = country.alpha_2
        #         name.save()
        #     else:
        #         name.delete()
        #         print(f"Code not found for {name}")
    with open('chat_openai/language.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data['data']:
        full_name = item['name']


        dialect, created = Language.objects.get_or_create(
            _id=item['_id'],
            defaults={
                'name': full_name,
            }
        )

        if created:
            print(f'Added new Language: {dialect.name}')
        else:
            print(f'Language already exists: {dialect.name}')