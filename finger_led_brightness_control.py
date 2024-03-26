import math
import time

import cv2
from cvzone.HandTrackingModule import HandDetector
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
from pyfirmata import Arduino, util


def main_app():
    # Arduino setup
    arduino_port = "COM3"
    board = Arduino(arduino_port)
    it = util.Iterator(board)
    it.start()

    # Define the pins for LEDs
    led_pin = 9  # Use a PWM pin
    board.get_pin('d:{}:p'.format(led_pin))
    board.digital[led_pin].write(1)
    time.sleep(1)
    board.digital[led_pin].write(0)
    time.sleep(1)

    # VIDEO SETUP
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # VOULUME CONTROL INIT
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    vol_range = volume.GetVolumeRange()
    min_vol, max_vol = vol_range[0], vol_range[1]
    print('min:{}, max:{}'.format(min_vol, max_vol))

    detector = HandDetector(maxHands=1, detectionCon=0.8)
    while True:
        # INIT WEBCAM
        success, captured_img = cap.read()

        hands, hand_img = detector.findHands(captured_img, draw=True, flipType=True)

        if hands:
            hand = hands[0]

            # Get distance between thumb and index finger
            thumb_tip = hand["lmList"][4]  # Thumb tip landmark
            index_tip = hand["lmList"][8]  # Index finger tip landmark

            # Calculate distance between specific landmarks on the first hand and draw it on the image
            p1 = thumb_tip[0:2]
            p2 = index_tip[0:2]
            first_color = (126, 218, 38)
            second_color = (11, 144, 248)
            scale = 12

            x1, y1 = p1
            x2, y2 = p2
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            distance = math.hypot(x2 - x1, y2 - y1)

            cv2.circle(hand_img, (x1, y1), scale, first_color, cv2.FILLED)
            cv2.circle(hand_img, (x2, y2), scale, first_color, cv2.FILLED)
            cv2.line(hand_img, (x1, y1), (x2, y2), first_color, max(1, scale // 3))
            # middle circle
            cv2.circle(hand_img, (cx, cy), scale, first_color, cv2.FILLED)

            # print("Thumb to index distance:", distance)

            if (distance < 60):
                # CHANGE THE MIDLE CIRCLE COLOR WHEN DISTANCE IS LESS THAN 60PX
                cv2.circle(hand_img, (cx, cy), scale, second_color, cv2.FILLED)

            vol_percent = int(np.interp(distance, [60, 300], [0, 100]))
            led_brightness = np.interp(distance, [60, 300], [0, 255])
            # Display volume level on image
            cv2.putText(hand_img, f"Volume: {int(vol_percent)}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(hand_img, f"led PWM: {int(led_brightness)} ", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Adjust LED brightness based on distance
            print(f'brightness : {int(led_brightness)}')
            board.digital[led_pin].write(led_brightness / 255.0)
            time.sleep(0.1)

            # Hand range 50 - 300
            # Volume Range -65 - 0

            vol = np.interp(distance, [60, 300], [min_vol, max_vol])
            # print(vol)

            #DECOMMENTER POUR CONTROLLER LE VOLUME DE WINDOWS
            # volume.SetMasterVolumeLevel(vol, None)

        cv2.imshow('image', hand_img)

        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break
        # cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main_app()
