from drive import DriveSystem, emotion_poles, decay_loop
import threading, time, os 

def decay_loop(drive):
    while True:
        drive.update()
        print_meters(drive)
        time.sleep(1)  # Wait for 1 second


def print_meters(drive):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console

    # Print the drive meter
    drive_meter_bar = int(abs(drive.drive_meter) * 20)
    drive_meter_display = "█" * drive_meter_bar + "░" * (20 - drive_meter_bar)
    print(f"Drive Meter: [{drive_meter_display}] {drive.drive_meter:.2f}")

    # Print the perception meters
    perception_meter_display = []
    for meter_name, meter_value in drive.perception_meter.items():
        meter_bar = int(meter_value * 20)
        meter_display = "█" * meter_bar + "░" * (20 - meter_bar)
        perception_meter_display.append(f"{meter_name.capitalize()}: [{meter_display}] {meter_value:.2f}")

    reaction_meter_display = []
    for meter_name, meter_value in drive.response_meters.items():
        meter_bar = int(meter_value * 20)
        meter_display = "█" * meter_bar + "░" * (20 - meter_bar)
        reaction_meter_display.append(f"{meter_name.capitalize()}: [{meter_display}] {meter_value:.2f}")
    print("\n".join(perception_meter_display))
    print("\n")
    print("\n".join(reaction_meter_display))

    # Wait for a short duration before refreshing
    time.sleep(0.1)

def main():
    # Create an instance of the DriveSystem class
    drive_system = DriveSystem()
    thread = threading.Thread(target=decay_loop, args=(drive_system,), daemon=True)
    thread.start()
        # Define a mapping between keys and intensities
    key_mapping = {
        'a': 1, 's': 2, 'd': 3, 'f': -1, 'g': -2, 'h': -3,  # emotion1
        'q': 1, 'w': 2, 'e': 3, 'r': -1, 't': -2, 'y': -3,  # emotion2
    }

    print("Press 'a', 's', 'd', 'f', 'g', 'h' for emotion1 intensities")
    print("Press 'q', 'w', 'e', 'r', 't', 'y' for emotion2 intensities")
    print("Press 'x' to exit")

    while True:

        #drive_system.print_meters()
        key = input("Enter a key: ").lower()

        if key == 'x':
            break

        if key in key_mapping:
            intensity = key_mapping[key]
            if key in ['a', 's', 'd', 'f', 'g', 'h']:
                drive_system.percieve_emotions("emotion1", intensity)
            else:
                drive_system.percieve_emotions("emotion2", intensity)

        else:
            print("Invalid key. Try again.")

if __name__ == "__main__":
    main()
