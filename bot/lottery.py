import random

from .models import Event, Participant, ResultLottery


def lottery(id):
    participants = Participant.objects.filter(game_id=id)
    print(participants)
    shuffled_participants = list(participants)
    random.shuffle(shuffled_participants)
    user_names = [participant.name for participant in shuffled_participants]
    user_pairs = list(zip(user_names, user_names[1:] + [user_names[0]]))
    ResultLottery.objects.get_or_create(giver_name=user_pairs[0][1],
                                        receiver_name=user_pairs[1][1])