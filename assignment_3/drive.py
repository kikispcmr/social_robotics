import os, time
import numpy as np 
emotion_poles = {
    "love and grief" : "emotion1",
        "agression and submission" : "emotion2",
}

class DriveSystem():

    def __init__(self):
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
            "postive": 0,
            "neutral" : 0, 
            "negative" : 0

        }

    def sig(self, x):
        return 1/(1 + np.exp(-x))

    # INTENSITIES 
    # Function that determins how perceptual input affects the perceptual bars
    def emotion_function(self, intensity, perceptual_bar):
        # Map intensity to a value between -1 and 1
        intensity_factor = min(max(intensity / 3, -1), 1)

        # Update the perception meter with the intensity factor
        self.perception_meter[perceptual_bar] = max(
            min(self.perception_meter[perceptual_bar] + intensity_factor, 1), 0.01)

    # Function that updates the bars based on the perceptual input
    def percieve_emotions(self, emotion_group, intensity):
        if emotion_poles[emotion_group] == "emotion1":
            self.emotion_function(intensity, "emotion1")
        elif emotion_poles[emotion_group] == "emotion2":
            self.emotion_function(intensity, "emotion2")

    def perceptual_decay(self):
        # Decay the perception meter intensity
        for key in self.perception_meter:
            self.perception_meter[key] = max(self.perception_meter[key] - 0.01, 0.01)

    def update_drive(self):
        emotion_difference = self.perception_meter["emotion1"] - self.perception_meter["emotion2"]
        emotion_dominance = abs(emotion_difference)

        drive_factor = emotion_dominance ** 2

        if emotion_difference > 0:
            self.drive_meter = min(drive_factor, 1)
        else:
            self.drive_meter = max(-drive_factor, -1)

    def print_meters(self):
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

        print("\n".join(perception_meter_display))

        # Wait for a short duration before refreshing
        time.sleep(0.1)




