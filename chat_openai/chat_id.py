import random 
import string

def generate_chat_id(length=30):
        if length < 26:  # Minimum length check
            raise ValueError("Length must be at least 26 for the specified format.")

        # Generate a random alphanumeric string
        letters_and_digits = string.ascii_letters + string.digits
        random_chars = random.choices(letters_and_digits, k=length)

        # Insert dashes at the specified positions
        # Format: xxxx-xxxxxx-xxxxx-xxxxxx-xxxxx-xxxx
        formatted_chat_id = (
            ''.join(random_chars[:4]) + '-' +
            ''.join(random_chars[4:10]) + '-' +
            ''.join(random_chars[10:15]) + '-' +
            ''.join(random_chars[15:21]) + '-' +
            ''.join(random_chars[21:26]) + '-' +
            ''.join(random_chars[26:])
        )
        return formatted_chat_id