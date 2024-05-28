# aruco id mapping - 12 cards
emotion_cards = {
    0: ("serenity", 1, "emotion1"),
    1: ("joy", 2, "emotion1"),
    2: ("ecstasy", 3, "emotion1"),
    3: ("pensiveness", -1, "emotion1"),
    4: ("sadness", -2, "emotion1"),
    5: ("grief", -3, "emotion1"),
    6: ("annoyance",-1, "emotion2"),
    7: ("anger",-2, "emotion2"),
    8: ("rage",-3, "emotion2"),
    9: ("apprehension",1, "emotion2"),
    10: ("fear",2, "emotion2"),
    11: ("terror",3, "emotion2")
}

emotion_poles = {
    "love and grief" : "emotion1",
    "agression and submission" : "emotion2",
}

negative_emotions = {"sadness", "grief", "annoyance", "anger", "rage", "apprehension", "fear", "terror"}

positive_emotions = {"serenity", "joy", "ecstasy"}
