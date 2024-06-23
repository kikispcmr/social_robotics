

questions = [
(
"So tell me, what is Human Geography, its how we interact with the ...?",
["earth"],
"Wow we have a good listener! Let's move on to the next question",
"I'll give you a clue, it's the planet we live on.",
),
("What is the capital of the Netherlands?",
 ["Amsterdam"],
 "Great! Let's move on to the next question",
 "It's a city famous for its canals and tulips.",
 ),
("What is the capital of Sweden?",
 ["Stockholm"],
    "Great! Let's move on to the next question",
 "Aww good guess. It's a city known for vikings and meatballs!",
),
("What country has the greatest population?", 
 ["India"],
"India recently overtook China as the most populous country in the world.",),
 "Close, but not quite. It used to be China but now another country overtook it!",
]
"""
A list of tuples containing questions, expected answers, and feedback messages related to Human Geography.

Each tuple contains the following elements:
    0: The question text (str)
    1: A list of expected answers (list of str)
    2: The feedback message for a correct answer (str)
    3: The feedback message for an incorrect answer (str, optional)
"""



harder_questions = [
("What is the smallest country in the world by land area? Is it the Monaco?",
False,
"You got it! Vatican City, with an area of just 0.17 square miles, is the smallest internationally recognized independent state in the world.",
"The smallest country in the world by land area is actually Vatican City, an independent city-state surrounded by Rome, Italy.",
),
("Is the pacific the largest in the world?",
True,
"Excellent! The Pacific Ocean is the largest and deepest of the world's oceans, covering about 30% of the Earth's surface.",
"The correct answer is the Pacific Ocean, which is larger than the Atlantic, Indian, and Arctic Oceans combined.",
),
("Are we the greatest cause of Global Warming?",
True,
"That's right! Greenhouse gas emissions from human activities like burning fossil fuels is why the planet is warming up.",
"I'll give you a clue, it's all about.",
),
("Does Methene gas make up the largest percentage of greenhouse gas emissions?",
False,
"Correct! Carbon dioxide is what accounts for about 76% of total greenhouse gas emissions from human activities.",
"While other gases like methane and nitrous oxide contribute to greenhouse gas emissions, carbon dioxide makes up the largest percentage.",
)
]
"""
A list of tuples containing questions, expected answers, and feedback messages related to Human Geography.

Each tuple contains the following:
    0: The question text (str)
    1: The expected answer (bool)
    2: The feedback message for a correct answer (str)
    3: The feedback message for an incorrect answer (str)
"""

capital_aruco = [
(
"If Amsterdam is in the middle, where is Groningen?",
1,
"Good job! Groningen is in the North of the Netherlands.",
),
(
"Now where would Eindhoven be?",
2,
  "That's right! Eindhoven is in the South of the Netherlands.",
),
(
"What about Rotterdam?",
2,
"Excellent job! Let's try something a bit harder",
),
]
"""
A list of tuples containing questions, expected answers, and feedback messages related to the capital cities of the Netherlands using Aruco cards.

Each tuple contains the following elements:
    0: The question text (str)
    1: The expected Aruco card ID (int)
    2: The feedback message for a correct answer (str)
"""

aruco = [
(
"From Groningen, which is closer Amsterdam or Rotterdam?",
4,
"Great! Let's move on to the next question.",
),
(
"From Amsterdam, which is closer Groningen or Eindhoven?",
2,
"Great! Let's move on to the next question.",
),
(
"From Groningen, which is closer Eindhoven or Rotterdam?",
4,
"Excellent job! You've completed the Human Geography lesson.",
),
]
"""
Tuples containing questions, expected answers, and feedback messages related to the relative distances between cities in the Netherlands using Aruco cards.

Each tuple contains the following elements:
    0: The question text (str)
    1: The expected Aruco card ID (int)
    2: The feedback message for a correct answer (str)
"""

intro = [
 "Welcome! We're going to be learning all about Human Geography today.",
 "The part of Geography all to do about us and our relationship with the Earth!",
 "We'll learn about cities, how we effect the Earth and more!",
]
"""
Intro for section 1 and 2.
"""

dialogue = [
 "Okay, let's move on to the next section.",
 "We talked all about these cities, let's play with some Aruco cards.",
 "We talked about some big cities in the Netherlands, but do you know what is further?",
 "You have four Aruco cards in front of you, 1 is for Amsterdam, 2 is for Groningen, 3 is for Eindhoven, 4 is for Rotterdam.",
]
"""
Intro for section 3.
"""

capital_section_intro = [
 "A big part of human geography is all about cities. Let's look at the Netherlands!",
 "You should be very familiar with the Netherlands. You have two Aruco cards, one for North, and one for South",
]
"""
Intro for section 4.
"""
