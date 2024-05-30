# DriveSystem Simulation for Emotional Response

This script simulates an emotional response system using a DriveSystem class. It is designed to interact with a robot to provide dynamic and empathetic emotional responses based on perceived inputs.

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

1. **Detection**:
   - The robot detects a participant's face and starts the interaction.
   - The robot asks true/false questions and interactive Aruco card questions.

2. **Emotion Processing**:
   - Detected emotions are processed using the `DriveSystem` class.
   - The system updates its state based on the perceived inputs.

3. **Response**:
   - The robot then expresses the appropriate emotional movement based on the calculation carried out.

Enjoy!
