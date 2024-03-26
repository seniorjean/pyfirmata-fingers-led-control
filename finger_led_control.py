import cv2
from cvzone.HandTrackingModule import HandDetector
from pyfirmata import Arduino, util
import time

def mainApp():
    # Arduino setup
    arduino_port = "COM3"  # Change this to your Arduino port
    board = Arduino(arduino_port)
    it = util.Iterator(board)
    it.start()

    # VIDEO SETUP
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

    detector = HandDetector(maxHands=1,detectionCon=0.8)

    # Define the pins for LEDs
    led_pins = [2, 3, 4, 5, 6]

    # Set the pin mode for each LED pin
    for pin in led_pins:
        board.get_pin('d:{}:o'.format(pin))

    while True:
        # INIT WEBCAM
        success, captured_img = cap.read()

        hands, hand_img = detector.findHands(captured_img)
        for pin in led_pins:
            board.digital[pin].write(0)
        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            finger_count = fingers.count(1)

            print("Number of fingers raised:", finger_count)

            # Turn on corresponding LEDs based on finger count
            for pin in led_pins:
                board.digital[pin].write(0)  # Turn off all LEDs

            for i in range(finger_count):
                board.digital[led_pins[i]].write(1)  # Turn on LEDs based on finger count

        cv2.imshow('image', hand_img)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break
        # cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    mainApp()

