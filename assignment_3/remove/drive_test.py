from drive import DriveSystem, emotion_poles 
import threading, time, os 

def decay_loop(drive):
    while True:
        drive.update_all_meters()
        drive.print_meters()
        time.sleep(1)  # Wait for 1 second


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
