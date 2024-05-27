import numpy as np


emotion_poles = {
    "love and grief" : "emotion1",
    "agression and submission" : "emotion2",
}

class DriveSystem():
    """
    This class represents a DriveSystem which simulates an emotional response system.

    Attributes:
    - drive_meter (float): A measure of the system's current emotional drive.
    - perception_meter (dict): A dictionary mapping emotions to their current perceived intensity.
    - response_meters (dict): A dictionary mapping emotional responses to their current intensity.
    - last_response (int): A counter for the last emotional response.
    """
    def __init__(self):
        """
        Initializes a new instance of the DriveSystem class.
        """
        # DRIVE BARS
        self.drive_meter = 0

        # PERCEPTUAL BARS
        # Decay the perception meter intensity
        self.perception_meter = {
            "emotion1": 0 ,  
            "emotion2" : 0, 
        }

        # RESPONSE BARS
        self.response_meters = {
            "positive": 0,
            "neutral" : 0, 
            "negative" : 0

        }

        self.last_response = 100000000

    def sig(self, x: float) -> float:
        """
        Calculates the sigmoid of a number.

        Args:
        - x (float): The number to calculate the sigmoid of.

        Returns:
        - float: The sigmoid of the number.
        """
        return 1/(1 + np.exp(-x))

    def update_all_meters(self) -> None | str:
        """
        Updates all meters and returns the selected emotion if the last response counter reaches 0.

        This method performs the following steps:
        - Calls the perceptual_decay method to decay the perception meter.
        - Calls the update_drive method to update the drive meter.
        - Calls the update_response_meters method to update the response meters.
        - Calls the decay_response_meters method to decay the response meters.
        - Decreases the last response counter by 1.
        - If the last response counter reaches 0, it resets the counter to a large number and selects an emotion using the emotion_selector method.
        """
        outcome = None
        self.perceptual_decay()
        self.update_drive()
        self.update_response_meters()
        self.decay_response_meters()
        self.last_response -= 1
        if self.last_response == 0:
            self.last_response = 100000000
            outcome = self.emotion_selector()
            print(self.emotion_selector())

        return outcome

    # INTENSITIES 
    # Function that determins how perceptual input affects the perceptual bars
    def emotion_function(self, intensity: float, perceptual_bar: str) -> None:
        """
        Updates the perception meter based on the intensity of the perceived emotion.

        This method performs the following steps:
        - Maps the intensity to a value between -1 and 1.
        - Updates the perception meter with the intensity factor.
        """
        # Map intensity to a value between -1 and 1
        intensity_factor = min(max(intensity / 3, -1), 1)
        # Update the perception meter with the intensity factor
        self.perception_meter[perceptual_bar] = max(
            min(self.perception_meter[perceptual_bar] + intensity_factor, 1), 0.01)

    # Function that updates the bars based on the perceptual input
    def percieve_emotions(self, emotion_group: str, intensity: float) -> None:
        """
        Updates the perception meter based on the perceived emotion and its intensity.

        This method performs the following steps:
        - Sets the last response counter to 3.
        - If the perceived emotion is 'emotion1', it updates the 'emotion1' perception meter with the intensity.
        - If the perceived emotion is 'emotion2', it updates the 'emotion2' perception meter with the intensity.
        """
        # This dictates how many seconds until it chooses an emotion
        print("D: ", emotion_group)
        self.last_response = 3
        if emotion_group == "emotion1":
            self.emotion_function(intensity, "emotion1")
        elif emotion_group == "emotion2":
            self.emotion_function(intensity, "emotion2")

    def perceptual_decay(self) -> None:
        """
        Decays the perception meter intensity over time.

        This method performs the following steps:
        - For each key in the perception meter, it decreases the intensity by 0.10, but not below 0.01.
        """
        # Decay the perception meter intensity
        for key in self.perception_meter:
            self.perception_meter[key] = max(self.perception_meter[key] - 0.10, 0.01)

    def update_drive(self) -> None:
        """
        Updates the drive meter based on the difference between the perceived emotions.

        The drive meter is updated based on the square of the absolute difference between the perceived intensities of 'emotion1' and 'emotion2'.
        If the difference is between 0.1 and 0.5, the drive meter is decreased.
        If the difference is greater than 0.5, the drive meter is increased.
        If the difference is not in these ranges, the drive meter is decreased by a small constant.
        """
        emotion_difference = self.perception_meter["emotion1"] - self.perception_meter["emotion2"]
        emotion_difference= abs(emotion_difference)

        drive_factor = emotion_difference ** 2
        if emotion_difference < 0.5 and emotion_difference > 0.1:
                self.drive_meter = self.sig(self.drive_meter - drive_factor)
        elif emotion_difference > 0.5:
            self.drive_meter = self.sig(self.drive_meter + drive_factor)
        else:
        self.drive_meter = max(self.drive_meter - 0.1, 0.01)

    def update_response_meters(self) -> None:
        """
        Updates the response meters based on the current drive meter.

        If the drive meter is less than 0.33, the 'negative' response meter is increased.
        If the drive meter is between 0.33 and 0.66, the 'neutral' response meter is increased.
        If the drive meter is greater than 0.66, the 'positive' response meter is increased.
        """
        if self.drive_meter >= 0 and self.drive_meter < 0.33:
            self.response_meters["negative"] = min(self.response_meters["negative"] + 0.1, 1) 
        elif self.drive_meter >= 0.33 and self.drive_meter < 0.66:
            self.response_meters["neutral"] = min(self.response_meters["neutral"] + 0.1, 1) 
        elif self.drive_meter >= 0.66:
            self.response_meters["positive"] = min(self.response_meters["positive"] + 0.1, 1) 

    def decay_response_meters(self) -> None:
        """
        Decays the response meters over time.

        If the drive meter is greater than or equal to 0.33, the 'negative' response meter is decreased.
        If the drive meter is less than or equal to 0.66, the 'positive' response meter is decreased.
        If the drive meter is not in these ranges, the 'neutral' response meter is decreased.
        """
        if self.drive_meter >= 0.33:
            self.response_meters["negative"] = max(self.response_meters["negative"] - 0.1, 0.01)
        if self.drive_meter <= 0.66: 
            self.response_meters["positive"] = max(self.response_meters["positive"] - 0.1, 0.01)
        if self.drive_meter <= 0.33 or self.drive_meter >= 0.66:
            self.response_meters["neutral"] = max(self.response_meters["neutral"] - 0.1, 0.01)


    def emotion_selector(self) -> str:
        """
        Selects the emotion with the highest response meter.

        This method iterates over the response meters and selects the emotion with the highest value. 
        If multiple emotions have the same highest value, it selects the first one it encounters.

        Returns:
        - str: The name of the emotion with the highest response meter.
        """
        max_val = 0
        max_name = ""
        for name, val in self.response_meters.items():
            if max_val < val:
                max_val = val
                max_name = name 

        return max_name



