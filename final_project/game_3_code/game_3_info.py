
encouragement_sentences = [
    "You're almost there! Keep up the good work.",
    "I can see how hard you're trying. That's what matters most.",
    "Don't give up! Every challenge is an opportunity to grow.",
    "You've got this! I believe in your abilities.",
    "Mistakes are just stepping stones to success. Keep going!"
]

positive_feedback_sentences = [
    "Excellent job!",
    "That's impressive! Keep up the great work.",
    "Fantastic! Your geography knowledge is top-notch.",
    "Brilliant! Your knowledge is truly remarkable.",
    "Well done! You're a geography whiz."
]

score_feedback = {
    (0, 3): "You did well, but there's room for improvement. Keep practicing and you'll get even better!",
    (4, 6): "Great job! You have a good grasp of geography. Keep up the good work!",
    (7, 9): "Excellent work! Your knowledge of geography is impressive. You're almost a geography expert!",
    (10, 10): "Perfect score! You're a geography master! Fantastic job!"
}

flag_cards = {
    1: ("Sweden", "a blue background with a golden yellow Nordic cross that extends to the edges."),
    2: ("Latvia", "a dark red background with a narrow white horizontal stripe in the middle."),
    3: ("Netherlands", "three horizontal stripes of equal size: red at the top, white in the middle, and blue at the bottom."),
    4: ("Cyprus", "a white background with a copper-colored silhouette of the island in the center above two crossed green olive branches."),
    5: ("Poland", "two equal horizontal bands of white on the top and red on the bottom.")     
    }


questions = [
    (
        "Over 50'%' of Latvia's territory is covered by forests",
        True,
        "Latvia is one of the greenest countries in Europe.",
    ),
    (
        "The Netherlands has the highest population density in Europe.",
        True,
        "Despite its small size, the Netherlands is densely populated.",
    ),
    (
        "Sweden is west of Norway genographically.",
        False,
        "Sweden is located to the east of Norway, not the west. The two countries share a long border.",
    ),
    (
        "Poland is home to the world’s largest castle by area.",
        True,
        "Malbork Castle in Poland is the largest castle by area in the world.",
    ),
    (
        "The city Nicosia in Cyprus is the only capital city in the world divided between two nations.",
        True,
        "Nicosia is divided between the Greek Cypriot south and the Turkish Cypriot north.",
    ),
    (
        "The Polish are the tallest people in the world.",
        False,
        "Actually the Dutch are the tallest people in the world, with an average height of 175.62 cm.",
    ),
]

# aruco id mapping - 12 cards
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