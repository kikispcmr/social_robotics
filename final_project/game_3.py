from twisted.internet.defer import inlineCallbacks
#from autobahn.twisted.component import Component, run
from autobahn.twisted.util import sleep

flag_cards = {
    1: ("Sweden", "idk"),
    2: ("Latvia", "idk"),
    3: ("Netherlands", "idk"),
    4: ("Cyprus", "idk"),
    5: ("Poland", "idk")     
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
        "Sweden is west of Norway genographically",
        False,
        "Sweden is located to the east of Norway, not the west. The two countries share a long border.",
    ),
    (
        "Poland is home to the world’s largest castle by area.",
        True,
        "Malbork Castle in Poland is the largest castle by area in the world.",
    ),
    (
        "Nicosia is the only capital city in the world divided between two nations.",
        True,
        "Nicosia is divided between the Greek Cypriot south and the Turkish Cypriot north.",
    ),
    (
        "The Polish are the tallest people in the world.",
        False,
        "Actually the Dutch are actually the tallest people in the world, with an average height of 175.62 cm.",
    ),
]

def smart_question_binary(session, question):
    """
    Asks a binary (True/False) question to the user and provides feedback based on the user's answer.
    """
    correct = False
    yield sleep(1)
    answer = yield session.call(
        "rie.dialogue.ask",
        question=question[0],
        answers={
            "true": ["true", "yes", "ja", "tru"],
            "false": ["false", "no", "nej", "fls"],
        },
    )
    yield sleep(1)
    _ = yield session.call("rie.dialogue.stt.read", time=6000)

    if (answer == "true" and question[1]) or (answer == "false" and not question[1]):
        # Nod yes
        session.call(
            "rom.actuator.motor.write",
            frames=[
                {"time": 400, "data": {"body.head.pitch": 0.15}},
                {"time": 1200, "data": {"body.head.pitch": -0.15}},
                {"time": 2000, "data": {"body.head.pitch": 0.15}},
                {"time": 2400, "data": {"body.head.pitch": 0.0}},
            ],
            force=True,
        )
        correct = True
        text = "That is correct." + question[2]
        yield session.call("rie.dialogue.say", text=text)
    elif (answer == "true" and not question[1]) or (answer == "false" and question[1]):
        yield session.call("rie.dialogue.say", text="That is incorrect.")

    return correct



def touched(frame):
    if ("body.head.front" in frame["data"] or "body.head.middle" in frame["data"] or "body.head.rear" in frame["data"]):
        print("touched") 


class CardUsage:
    def __init__(self, session):
        self.session = session
        

    @inlineCallbacks
    def ask_flag_card_question(self):
        #session.call("rie.vision.card.stream")
        # we ask the question based on animal_cards mapping
        
        for card_id, (country, fact) in flag_cards.items():
            correct = False
            attempts = 0
            max_attempts = 2  # set a max number of attempts per question
            question = f"What does the national flag of {country} look like?"

            while not correct:
                if attempts > 0 and attempts < 2:  # ask the question, if not first attempt, provide feedback
                    yield self.session.call("rie.dialogue.say", text="Try one more time. " + question)
                elif attempts > 1:
                    yield self.session.call("rie.dialogue.say", text="The national flag of {country} has {fact}." + question)
                else:
                    yield self.session.call("rie.dialogue.say", text=question)

                correct = yield self.wait_for_correct_flag(self.session, card_id)

                print("exited")
                if correct:
                    yield self.session.call("rie.dialogue.say", text=f"Correct! That is the national flag of {country}. Let's try another country !")
                else:
                    yield self.session.call("rie.dialogue.say", text="That's not the correct flag!")
                
                attempts += 1

    
    @inlineCallbacks
    def wait_for_correct_flag(self, correct_card_id):
        card_detected = yield self.detect_card()
        yield self.session.call("rie.vision.card.stream")
        return card_detected == correct_card_id

    
    def detect_card(self):
        print("entered")
        # detect the shown card
        card_detected = yield self.session.call("rie.vision.card.read")
        print("card detected : ", card_detected[0]['data']['body'][0][5])
        card_detected = card_detected[0]['data']['body'][0][5]

        return card_detected



class Levels:
    def __init__(self, session, score, card_usage):
        self.session = session
        self.score = score
        self.card_usage = card_usage
    
    @inlineCallbacks
    def easy(self):
        yield self.session.call("rie.dialogue.say", text="I will ask you a question and you should pick which aruco card is the correct answer!")
        yield self.card_usage.ask_flag_card_question(self.session)
        self.score = 2

    @inlineCallbacks
    def medium(self):
        for question in questions[:-1]:
            if (yield smart_question_binary(self.session, question)):
                self.score += 1
        
        if self.score < 4:
            yield self.session.call("rie.dialogue.say", text="You are doing so well, you deserve a bonus question! Answer the following extra bonus question correctly for an additional point?")
            if (yield smart_question_binary(self.session, questions[-1])):  # Ask the last question separately
                self.score += 1



    @inlineCallbacks
    def hard(self):
        # Hard Level
        yield self.session.call("rie.dialogue.config.language", lang="en")
        # Say something with the ReadSpeaker voice in English
        yield self.session.call("rie.dialogue.say", text="Guess the next language I am speaking? Name the country and then match it to one of the flag cards in front of you! Let's start!")

        yield self.session.call("rie.dialogue.config.language", lang="nl")
        # Say something with the ReadSpeaker voice in English
        yield self.session.call("rie.dialogue.say", text="Hallo! Ik ben hier om je aardrijkskunde te leren! Welk land spreekt deze taal?")
        detected_card = self.card_usage.detect_card()
        if detected_card == 3:
            self.score += 1

        yield self.session.call("rie.dialogue.config.language", lang="pl")
        yield self.session.call("rie.dialogue.say", text="Cześć! Nazywam się Alpha Mini i jestem tutaj, aby nauczyć Cię geografii! W jakim kraju mówi się tym językiem?")
        detected_card = self.card_usage.detect_card()
        if detected_card == 5:
            self.score += 1

        yield self.session.call("rie.dialogue.config.language", lang="sv")
        yield self.session.call("rie.dialogue.say", text="Hej, jag är här för att lära dig lite geografi! Vilket land talar detta språk?")
        if detected_card == 5:
            self.score += 1

        yield self.session.call("rie.dialogue.config.language", lang="en")
        










# vics game individual part
@inlineCallbacks
def start_game(session):
    yield session.call("rie.dialogue.say", text="")
    score = 0
    aruco_card_usage = CardUsage(session)
    game_levels = Levels(session, score, aruco_card_usage)

    # Easy difficulty part
    yield session.call("rie.dialogue.say", text="Guess all of the coutries national flags atleast once and score 3 points! Are you ready?")
    answers = {"yes": ["yeah", "yes", "ye", "okay"], "no": ["no", "nah", "nope"]} 
    answer = yield session.call("rie.dialogue.ask", question="Guess all of the coutries national flags atleast once and score 3 points! Are you ready?", answers=answers)

    if answer == "yes": 
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!") 
        yield game_levels.easy()
    elif answer == "no": 
        yield session.call("rie.dialogue.say", text="Okay! Then let me know when you want to begin by touching my head!") 
        # Touch subscribte
        session.subscribe(touched, "rom.sensor.touch.stream")
        yield session.call("rom.sensor.touch.stream")  # <- touch interaction
        yield session.call("rie.dialogue.say", text="Awesome! Let's begin!")
        yield game_levels.easy()
    else: 
        yield session.call("rie.dialogue.say", text="Sorry, I couldn't hear you properly...")
    
    # Medium difficulty part
    yield session.call("rie.dialogue.say", text="Well done! Now that you have correctly answered all of the flag questions, let's move on to some trivia!" +
                       "This time I will add points to your score for every correct answer!")
    yield game_levels.medium()

    yield session.call("rie.dialogue.say", text="Now that you collected so many points. Let's try something different. I will speak in a language and you will have to guess what language out of the countries infront of you am I speaking?"
                       + "I hope you paid attention to the beginning of our game about the different national flags")
    
    # Final feedback
    yield session.call("rie.dialogue.say", text=f"You did amazing! Your knowledge of geography is impressive. Your final score is {game_levels.score} out of 10.")
    session.leave()

