from drive import DriveSystem, emotion_poles

def main():
    # Create an instance of the DriveSystem class
    drive_system = DriveSystem()

    # Define a mapping between keys and intensities
    key_mapping = {
        'a': 1, 's': 2, 'd': 3, 'f': -1, 'g': -2, 'h': -3,  # emotion1
        'q': 1, 'w': 2, 'e': 3, 'r': -1, 't': -2, 'y': -3,  # emotion2
    }

    print("Press 'a', 's', 'd', 'f', 'g', 'h' for emotion1 intensities")
    print("Press 'q', 'w', 'e', 'r', 't', 'y' for emotion2 intensities")
    print("Press 'x' to exit")

    while True:
        key = input("Enter a key: ").lower()

        if key == 'x':
            break

        if key in key_mapping:
            intensity = key_mapping[key]
            if key in ['a', 's', 'd', 'f', 'g', 'h']:
                drive_system.percieve_emotions("love and grief", intensity)
            else:
                drive_system.percieve_emotions("agression and submission", intensity)

            drive_system.update_drive()
            drive_system.print_meters()
        else:
            print("Invalid key. Try again.")

if __name__ == "__main__":
    main()
