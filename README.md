# Geography Trivia Question Game 

Engage children from ages 8 - 10 in an interactive trivia question game with a robot! The robot will ask a series of true/false and multiple-choice questions, provide feedback on the user's answers, and even offer additional trivia information related to the questions.

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

Our project will guide the user through a series of trivia questions, starting with a few true/false questions. After a few questions, the robot will ask the user if they want to try something harder. Depending on the reply, the question game will either try harder question based on previously mentioned trivia, or continue the original game. 

Enjoy!



