
"""
    Shared code

    A dictionary which contains emotion card ids with their respective emotions.

    Each key is an integer representing the card ID, and the value is a tuple containing:
        - Emotion name (str): The name of the emotion.
        - Emotion value (int): The numeric value associated with the emotion, where positive values represent positive emotions and negative values represent negative emotions.
        - Emotion type (str): A string representing the category or type of the emotion.

"""

emotion_cards = {
    17: ("serenity", 1, "emotion1"),
    16: ("joy", 2, "emotion1"),
    15: ("ecstasy", 3, "emotion1"),
    14: ("pensiveness", -1, "emotion1"),
    13: ("sadness", -2, "emotion1"),
    12: ("grief", -3, "emotion1"),
    6: ("boredom",-1, "emotion2"),
    7: ("disgust",-2, "emotion2"),
    8: ("loathing",-3, "emotion2"),
    9: ("acceptance",1, "emotion2"),
    10: ("trust",2, "emotion2"),
    11: ("admiration", 3, "emotion2")
}

emotion_poles = {
    "love and grief" : "emotion1",
    "remorse and submission" : "emotion2",
}

negative_emotions = {"sadness", "grief", "annoyance", "anger", "rage", "apprehension", "fear", "terror"}

positive_emotions = {"serenity", "joy", "ecstasy"}
