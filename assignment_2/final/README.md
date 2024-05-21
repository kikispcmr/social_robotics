# Geography Trivia Question Game 

Our interactive geography learning game for students aged 9-12 uses a social robot to create an engaging educational experience! The robot will ask a series of true/false questions and interactive aruco card questions, provide feedback on the user's answers, and even offer additional trivia information related to the questions.

## Prerequisites

Before running this script, you'll need to have the following:

1. Access to a robot from  [Robots in de Klas Portal](https://portal.robotsindeklas.nl).
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

The robot begins by detecting a participant's face and asking if they want to play. The child starts the game by touching the robot's head, which focuses their attention.

The game includes true/false questions with positive feedback for correct answers, including predefined clapping gestures and fun facts. Incorrect answers receive corrective feedback and encouragement. The robot also performs an iconic skiing gesture to illustrate a concept and uses predefined behaviors like dancing and waving to maintain engagement.

In the final phase, the child uses Aruco cards to match animals to their habitats, allowing for kinesthetic learning. This multimodal interaction aims to create an effective and enjoyable geography lesson.

Enjoy!



