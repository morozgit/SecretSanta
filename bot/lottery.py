import random

from .models import Participant


def lottery():
    participants = Participant.objects.all()
    shuffled_participants = list(participants)
    random.shuffle(shuffled_participants)
    user_pairs = list(zip(shuffled_participants, shuffled_participants[1:] + [shuffled_participants[0]]))
    for user_pair in user_pairs:
        print(*user_pair)