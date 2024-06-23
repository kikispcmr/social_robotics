positive_emotion = [
    # starting position
        {
            "time": 400,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 0,
                "body.arms.left.lower.roll": 0
            },
        },
        {
            "time": 1000,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 0.0,
                "body.arms.left.lower.roll": 0.0
            },
        },
        {
            "time": 1400,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 1.0,
                "body.arms.left.lower.roll": -1.0
            },
        },
        {
            "time": 1800,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": -1.0,
                "body.arms.left.lower.roll": 1.0
            },
        },
        {
            "time": 2200,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": 1.0,
                "body.arms.left.lower.roll": -1.0
            },
        },
                {
            "time": 2600,
            "data": {
                "body.arms.right.upper.pitch": -2.5,
                "body.arms.left.upper.pitch": -2.5,
                "body.arms.right.lower.roll": -1.0,
                "body.arms.left.lower.roll": 1.0
            },
        },
   ]
"""
A list of dictionaries representing a positive emotion animation sequence.

- "time": The time in milliseconds at which the animation frame should be executed.
- "data": A dictionary containing the joint positions.

The following positions are used:
- "body.arms.right.upper.pitch": The pitch angle of the right upper arm.
- "body.arms.left.upper.pitch": The pitch angle of the left upper arm.
- "body.arms.right.lower.roll": The roll angle of the right lower arm.
- "body.arms.left.lower.roll": The roll angle of the left lower arm.

The animation sequence starts with the arms in a neutral position and then moves them in a
waving motion to express a positive emotion.
"""

mapping = {
    "positive": positive_emotion,
}
"""
A dictionary mapping emotion names to animation sequences.

Keys:
    "positive": The animation sequence for a positive emotion.

Values:
    A list of dictionaries representing the animation sequence, as described in the
    `positive_emotion` variable.
"""
