from django.core.management.base import BaseCommand
from chat_openai.models import SuggestPromptsImageModel

class Command(BaseCommand):
    help = 'Adds a list of prompts to the database'

    def handle(self, *args, **kwargs):
        prompts = [

"A futuristic cityscape at dusk with neon lights and flying cars.",
"An underwater scene showing a city made entirely of coral.",
"A surreal landscape where the trees are made of crystals.",
"A medieval marketplace bustling with people, set in a forest.",
"A small, cozy cabin in a snowy landscape under the northern lights.",
"A steampunk version of Paris with airships and copper structures.",
"A fantasy map of an uncharted island with hidden treasures and mysterious creatures.",
"A robot chef cooking in a high-tech kitchen.",
"A whimsical garden with giant mushrooms and fairy-like creatures.",
"A space station orbiting a colorful nebula.",
"An ancient library with magical books and floating candles.",
"A cyberpunk street scene with neon signs and diverse characters.",
"A serene Zen garden with a koi pond and cherry blossoms.",
"A post-apocalyptic city reclaimed by nature.",
"A magical forest with bioluminescent plants and mythical animals.",
"An art gallery in space, showcasing intergalactic art pieces.",
"A Viking village during a festive celebration.",
"A bustling Moroccan souk filled with spices and textiles.",
"A surreal painting of a city where the buildings bend like in a Salvador Dali painting.",
"A futuristic sports arena hosting a zero-gravity game.",
"An elegant masquerade ball in an opulent 18th-century palace.",
"A charming street in Tokyo during cherry blossom season.",
"An old Western town with cowboys and saloons.",
"A fantasy scene showing a meeting of different mythical creatures.",
"A high-fashion photoshoot in an abandoned industrial setting.",
"A historical reenactment in an ancient Roman forum.",
"A traditional Indian wedding ceremony with vibrant colors and elaborate decorations.",
"A whimsical candy land with edible landscapes.",
"A deep-sea exploration scene with unknown marine life.",
"An enchanted forest clearing with a mystical portal.",
"A futuristic African city blending traditional architecture and modern technology.",
"A panoramic view of the Great Wall of China in autumn.",
"An art studio filled with impressionist style paintings and sculptures.",
"A traditional Japanese tea ceremony in a tranquil garden.",
"A bustling New York street scene in the roaring 1920s.",
"A fantasy scene of a knight battling a dragon.",
"A 1950s American diner with classic cars and jukebox.",
"A luxurious underwater hotel with glass walls showing the ocean.",
"A winter wonderland with ice sculptures and aurora borealis.",
"A scene from a Shakespearean play set in the Globe Theatre.",
"A lively Brazilian carnival with dancers and extravagant costumes.",
"A grand Egyptian pyramid construction site in ancient times.",
"A panoramic view of Machu Picchu at sunrise.",
"A large-scale ant farm showing an intricate network of tunnels and chambers.",
"An ancient Greek agora bustling with philosophers and artisans.",
"A modern cityscape with sustainable and eco-friendly architecture.",
"A 17th-century pirate ship in the midst of a battle at sea.",
"A Renaissance art studio with artists painting and sculpting.",
"A secret garden hidden behind an old, ivy-covered wall.",
"An alien marketplace on a distant planet with various interstellar species.",

            ]

        for prompt in prompts:
            SuggestPromptsImageModel.objects.create(prompt=prompt)
            self.stdout.write(self.style.SUCCESS(f'Successfully added prompt: "{prompt}"'))
