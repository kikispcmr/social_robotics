import numpy as np
import os, time
from typing import Any

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
        self.drive_meter = 0.5

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

    def sig(self, x: float) -> float:
        """
        Calculates the sigmoid of a number.

        Args:
        - x (float): The number to calculate the sigmoid of.

        Returns:
        - float: The sigmoid of the number.
        """
        return 1/(1 + np.exp(-x))

    def overwhelemed_check(self) -> bool:
        """
        Checks if any of the response meters is full (1.0).
        If any meter is full, the robot is considered overwhelmed.

        Returns:
        bool: True if the robot is overwhelmed, False otherwise.
        """
        for meter in self.response_meters:
            if self.response_meters[meter] == 1.0:
                return True
        return False

    def update_all_meters(self) -> Any:
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
        outcome  = None
        intensity = 0.5
        self.perceptual_decay()
        self.update_drive()
        self.update_response_meters()
        self.decay_response_meters()
        if self.overwhelemed_check():
            outcome, intensity = self.emotion_selector()

        return outcome, intensity

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
            min(self.perception_meter[perceptual_bar] + intensity_factor, 1), -1)

    # Function that updates the bars based on the perceptual input
    def perceive_emotions(self, emotion_group: str, intensity: float) -> None:
        """
        Updates the perception meter based on the perceived emotion and its intensity.

        This method performs the following steps:
        - Sets the last response counter to 3.
        - If the perceived emotion is 'emotion1', it updates the 'emotion1' perception meter with the intensity.
        - If the perceived emotion is 'emotion2', it updates the 'emotion2' perception meter with the intensity.
        """
        # This dictates how many seconds until it chooses an emotion
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
            if self.perception_meter[key] >= 0:
                self.perception_meter[key] = max(self.perception_meter[key] - 0.10, 0)
            else:
                self.perception_meter[key] = min(self.perception_meter[key] + 0.10, 0)



    def update_drive(self) -> None:
        """
        Updates the drive meter based on the current values of the perception meters for emotion1 and emotion2.

        The drive meter is adjusted according to the following rules:

        1. If the sum of emotion1 and emotion2 perception meters is 0:
            - If the current drive meter is less than 0.5, it is increased by 0.1 (up to a maximum of 0.5).
            - If the current drive meter is greater than 0.5, it is decreased by 0.1 (down to a minimum of 0.5).

        2. If the sum of emotion1 and emotion2 perception meters is negative:
            - The drive meter is decreased by the absolute value of the sum, but not below 0.

        3. If the sum of emotion1 and emotion2 perception meters is positive:
            - The drive meter is increased by the absolute value of the sum, but not above 1.
        """
        emotion_difference = self.perception_meter["emotion1"] + self.perception_meter["emotion2"]
        emotion_difference = emotion_difference
        if emotion_difference == 0:
            if self.drive_meter < 0.5:
                self.drive_meter = min(self.drive_meter + 0.1, 0.5)
            elif self.drive_meter > 0.5:
                self.drive_meter = max(self.drive_meter - 0.1, 0.5)
        elif emotion_difference < 0: 
            self.drive_meter = max(self.drive_meter - abs(emotion_difference), 0) 
        elif emotion_difference > 0:
            self.drive_meter = min(self.drive_meter + abs(emotion_difference), 1) 


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
        return max_name, max_val


    def print_meters(self):
        """
        Prints the current state of the drive meter, perception meters, and response meters to the console.

        This method clears the console and then prints the following information:

        1. Drive Meter: A bar representation of the current drive meter value, along with the numerical value.
        2. Perception Meters: A list of perception meters, each with a bar representation and numerical value.
        3. Response Meters: A list of response meters, each with a bar representation and numerical value.

        The bar representations are created using Unicode characters for filled (█) and empty (░) blocks.
        The length of the bar is proportional to the meter value, with a maximum length of 20 characters.
        """
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console

        # Print the drive meter
        drive_meter_bar = int(abs(self.drive_meter) * 20)
        drive_meter_display = "█" * drive_meter_bar + "░" * (20 - drive_meter_bar)
        print(f"Drive Meter: [{drive_meter_display}] {self.drive_meter:.2f}")

        # Print the perception meters
        perception_meter_display = []
        for meter_name, meter_value in self.perception_meter.items():
            meter_bar = int(meter_value * 20)
            meter_display = "█" * meter_bar + "░" * (20 - meter_bar)
            perception_meter_display.append(f"{meter_name.capitalize()}: [{meter_display}] {meter_value:.2f}")

        reaction_meter_display = []
        for meter_name, meter_value in self.response_meters.items():
            meter_bar = int(meter_value * 20)
            meter_display = "█" * meter_bar + "░" * (20 - meter_bar)
            reaction_meter_display.append(f"{meter_name.capitalize()}: [{meter_display}] {meter_value:.2f}")
        print("\n".join(perception_meter_display))
        print("\n")
        print("\n".join(reaction_meter_display))
        # Wait for a short duration before refreshing
        time.sleep(0.1)
