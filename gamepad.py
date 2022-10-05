import vgamepad as vg
import time

from tuner_audio.audio_analyzer import AudioAnalyzer
from tuner_audio.threading_helper import ProtectedList

frequency_queue = ProtectedList()

audio_analyzer = AudioAnalyzer(frequency_queue)
audio_analyzer.start()

nearest_note_number_buffered = 69
a4_frequency = 440

gamepad = vg.VX360Gamepad()

# press a button to wake the device up
gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
gamepad.update()

gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
gamepad.update()

time.sleep(30.0)

while (audio_analyzer.running):

    freq = frequency_queue.get()
    if freq is not None:

        # convert frequency to note number
        number = audio_analyzer.frequency_to_number(freq, a4_frequency)

        # calculate nearest note number, name and frequency
        nearest_note_number = round(number)

        note = audio_analyzer.number_to_note_name(nearest_note_number)

    match note:
        case 'C':
            print('C')
        case 'C#':
            print('C#')
        case 'D':
            print('D')
        case 'D#':
            print('D#')
        case 'E':
            print('E')
        case 'F':
            print('F')
        case 'F#':
            print('F#')
        case 'G':
            print('G')
        case 'G#':
            print('G#')
        case 'A':
            print('A')
        case 'A#':
            print('A#')
        case 'B':
            print('B')

    # press buttons and things
    #gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
    #gamepad.update()

    # release buttons and things
    #gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
    #gamepad.update()

    time.sleep(1.0)