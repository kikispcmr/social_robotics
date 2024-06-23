# Final project code

The final project is a geography game containing three mini-games, each with a separate theme and goal to teach the user, catered towards students aged 9 to 12. The file structure is divided into separate folders representing each mini-game and an extra folder for the shared code used between all mini-games. The shared code is code used from previous assignments.

## Prerequisites

Before running this script, you'll need to have the following:

1. Access to a robot from [Robots in de Klas Portal](https://portal.robotsindeklas.nl).
2. The robot's realm ID, which can be found on the aforementioned portal.

## Getting Started

1. Open the `main.py` file and locate the following line:

```python
wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"]}],
    realm="rie.6633488cc887f6d074f02eeb",  # Replace with your robot's realm ID
)
```

3. Replace `"rie.6633488cc887f6d074f02eeb"` with your robot's realm ID, which you can find on the [Robots in de Klas Portal](https://portal.robotsindeklas.nl).

4. Make sure you have the required Python dependencies installed, which can be found in the requirments.txt file. As of now, only `autobahn` and `twisted` are required.

5. Run the script using the following command:

```
python main.py
```

## How It Works

At the beginning of the game, the social robot asks the user to choose between three mini-games to play, providing a short description of each of them. Each mini-game corresponds to someone's individual part.

## Game 1 : Animals and continents (Individual part of Mathias)

The animal game is an educational dialogue experience designed to teach children about different animals and their habitats.
It is structured in two unique phases. The first phase is about recognizing the right continent based on the animal.
The child has to show the correct aruco card to the robot. The second phase is a series of true and false questions,
which further reinforces the facts given about each habitat, making use of the knowledge that the robot communicates
during the first phase. The robot guides the children and gives hints if they answer wrongly.
It also reacts positively or negatively based on the response.  
Throughout the game, the robot makes use of dialogue, gestures, and audio cues to maintain an engaging learning experience.

The card designs can be found in the Game 1 folder.

# The mapping of the Cards

Animals game:
1: Australia
2: Asia
3: Africa
4: Arctic
5: Antarctica

True or false:
6: True
7: False

---

## Game 2: Human Geography Basics

This mini-game aims to teach users about human geography. The general structure is split
in 4 parts, where each section builds of the last. Each section will provide a prompt allowing the user to skip the section if its too easy.

### Section 1:

Introduction to human geography and basic facts about the Netherlands, followed by a trivia game with keyword questions based on the introduction.

### Section 2:

Harder questions on higher-level facts. If the user gets 2 questions correct in a row, they are prompted to skip ahead. Appropriate animations are played for correct/incorrect answers.

### Section 3:

Capital-themed questions with ARUCO markers. The robot performs various motions and animations based on the user's responses.

### Section 4:

ARUCO questions with increasing difficulty. If the user gets 2 questions correct in a row, they are prompted to try something harder.

The game is divided into four progressive sections, each building upon the knowledge gained in the previous section. Animations are used throughout, portraying the robot as a fun yet knowledgeable teacher to ensure facts are treated as facts while providing an enjoyable experience for all baseline knowledge levels.

### Direction Mappings for section 3:

These mappings contain the ARUCO marker and the corresponding direction.

```md
1: North
2: South
```

### Capital City Mappings for section 4:

These mappings contain the ARUCO marker and the corresponding city.

```md
1: Rotterdam
2: Groningen
3: Eindhoven
4: Amsterdam
```

---

## Game 3 : Geography Challenge (Victorias Individual Part)

Game 3 is a Geography Challenge designed to test and improve the user's knowledge of national flags, trivia, and languages from Europe. The game is divided into three difficulty levels: easy, medium, and hard.

After completing all three levels, the user receives a final score and personalized feedback based on their performance. The robot then asks the user how they feel about completing the challenge and expresses empathy based on the user's emotional response, detected through Aruco cards representing different emotions.

Finally, the robot asks the user if they would like to play the game again to beat their high score.

### Easy Level

In the easy level, the user is presented with a series of questions about the national flags of different countries. The user must identify the correct flag by showing the corresponding Aruco card to the robot. The game provides feedback on whether the user's answer is correct or incorrect with motivating comments and hints. The user must correctly identifying all the flags to progress to the next level.

### Medium Level

In the medium level, the user is asked geography trivia questions related to European countries. For each correct answer, the user earns a point. The game provides feedback on the correctness of the user's answers and a bonus question if the users score is low.

### Hard Level

In the hard level, the robot speaks in different languages, and the user must guess which country the language belongs to by showing the corresponding flag Aruco card. The game provides feedback on whether the user's answer is correct or incorrect, and the user earns a point for each correct answer.

### Game 3 Aruco Card Mapping

The PDF file in the game_3_code folder contains the print-out version of the Aruco cards with Aruco markers and corresponding pictures for each Aruco marker.

#### Flag Mappings :

Flag mappings contain the aruco marker and the flag of the country.
1 : Sweden
2 : Latvia
3 : Netherlands
4 : Cyprus
5 : Poland
18: Spain

#### Emotion Mapping :

The emotion mappings contain aruco marker and the emotion as an emoji.

17: serenity
16: joy
15: ecstasy
14: pensiveness
13: sadness
12: grief
6 : boredom
7 : disgust
8 : loathing
9 : acceptance
10: trust
11: admiration

## Shared Code description

We allow the user to show Aruco cards to the robot, each representing different emotions. Based on the shown cards or an combination of them, the system calculates whether it is appropriate to express neutral, negative or positive emotion via a drive system, implemented in the DriveSystem class. It is designed to interact with a robot to provide dynamic and empathetic emotional responses based on perceived inputs.

The script uses a `DriveSystem` class which simulates an emotional response system based on the user input. The system updates its state based on perceived emotional inputs and provides appropriate empathetic responses.

### Key Components:

1. **DriveSystem Class**:
   The drive system calculates a suitable emotional response based on the emotions inputted to the robot by the user by showing aruco cards. I has three distinct parts, which can be thought of as equilibria affecting each other based on inputs. The first part is the perceptual meters, which encode perceived emotions into the drive. In addition, there are 12 different emotion intensities across two bipolar categories. According to the intensity values corresponding to specific emotional expressions - the perceptual meters update based on the emotion category and intensity, staying between -1 and 1. The overall absolute value of perceived emotions dictates the drift of the robot's drive. Conflicting emotions cancel out, while complementary emotions are summed and have a more significant impact. The main drive meter represents an equilibrium that shifts left or right based on inputs. It is segmented into negative (0 to 0.33), neutral (0.33 to 0.66), and positive (0.66 to 1.0) ranges. A corresponding response bar is updated by 0.1 for each time-step spent in a segment. Lastly, it is essential to note that at any time-step, where the robot does not perceive an input, all meters decay slowly to their base equilibrium at a pace of $-0.1$ per time-step.

2. **Emotion Mapping**:
   - The script maps various Aruco card IDs to specific emotions.
   - **Example Mapping**:
     ```python
     emotion_cards = {
         0: ("serenity", 1, "emotion1"),
         1: ("joy", 2, "emotion1"),
         2: ("ecstasy", 3, "emotion1"),
         3: ("pensiveness", -1, "emotion1"),
         ...
     }
     ```

### Flow of the system:

2. **Emotion Processing**:

   - Detected emotions are processed using the `DriveSystem` class.
   - The system updates its state based on the perceived inputs.

3. **Response**:
   - The robot then expresses the appropriate emotional movement based on the calculation carried out.

Enjoy!
