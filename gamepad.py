import vgamepad as vg
import time
import PySimpleGUI as sg
from threading import Thread
from tuner_audio.audio_analyzer import AudioAnalyzer
from tuner_audio.threading_helper import ProtectedList

thisdict ={}
frequency_queue = ProtectedList()

audio_analyzer = AudioAnalyzer(frequency_queue, minimum_volume = 800) #Pode-se mudar o volume mínimo usando set_minimum_volume
audio_analyzer.start()

nearest_note_number_buffered = 69
a4_frequency = 440

gamepad = vg.VX360Gamepad()

# press a button to wake the device up
a=vg.XUSB_BUTTON.XUSB_GAMEPAD_A
b=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE
gamepad.press_button(button=a)
gamepad.update()

gamepad.release_button(button=a)
gamepad.update()
time.sleep(0.5)


print("Audio Analizer Started")
note = None
def vgButton(button):
    match button:
        case "cima":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP
        case "baixo":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN
        case "esquerda":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT
        case "direita":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT
        case "A":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_A
        case "B":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_B
        case "X":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_X
        case "Y":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_Y
        case "Lb":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER
        case "Lt":#a
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_A
        case "Rb":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER
        case "Rt":#a
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_A

def buttonMap(button,nota):
    global noteC, noteCSharp, noteD, noteDSharp
    global noteF, noteFSharp, noteG, noteGSharp
    global noteA, noteAsharp, noteB, noteE
    
    
    
def interfaceButtonMap():
    botao = ["cima","baixo","esquerda","direita","A","B","X","Y","Lb","Lt","Rb","Rt"]
    notas = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
    agreeMap="s"
    
    print("Voce quer mapear os botoes?(s/n)")
    agreeMap = input()
    if(agreeMap == "n"):
        for i in range(12):
            thisdict[notas[i]] = vgButton(botao[i])
    else:
        for button in botao:
            agree="n"
            while(agree!="s"):
                print("Defina uma nota para o botao: ", button)
                nota = getNote()
                print("Esta eh a nota que voce quer, ", nota ,"para o botao",button, " ? (s/n)")
                agree = input()
            thisdict[nota] = vgButton(button)



def getNote():
    #while (audio_analyzer.running):
    notaAtual="No note"
    while (notaAtual == "No note"):

        freq = frequency_queue.get()    
        if freq is not None:
            # convert frequency to note number
            number = audio_analyzer.frequency_to_number(freq, a4_frequency)

            # calculate nearest note number, name and frequency
            nearest_note_number = round(number)

            note = audio_analyzer.number_to_note_name(nearest_note_number)
        else:
            note = None

        #if frequency_queue.elements[len(frequency_queue.elements) - 1] == None:
        #    note = None
        
        if(note == None):
            notaAtual = "No note"
        else:
            return note
        """
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
            case other:
                print('No note')
        """

        # press buttons and things
        #gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
        #gamepad.update()

        # release buttons and things
        #gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE)
        #gamepad.update()

        time.sleep(0.033) #30FPS
        
def clickButton():
    print("Audio Analizer Awaiting first value...")
    while (not audio_analyzer.running or frequency_queue.get() is None): #Só irá iniciar quando o volume mínimo for atingido
        time.sleep(0.5)
    print("Rodando")
    while (audio_analyzer.running):
        freq = frequency_queue.get()    
        if freq is not None:
            # convert frequency to note number
            number = audio_analyzer.frequency_to_number(freq, a4_frequency)

            # calculate nearest note number, name and frequency
            nearest_note_number = round(number)

            note = audio_analyzer.number_to_note_name(nearest_note_number)
        else:
            note = None

        if frequency_queue.elements[len(frequency_queue.elements) - 1] == None:
            note = None
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
            #case other:
            #    print('No note')
                
        if(note == None):
            notaAtual = "No note"
        else:
            gamepad.press_button(thisdict[note])
            gamepad.update()
            time.sleep(0.5) #30FPS
            # release buttons and things
            gamepad.release_button(thisdict[note])
            gamepad.update()
            time.sleep(0.5)
        
        time.sleep(0.033) #30FPS

interfaceButtonMap()
#t = Thread(target=clickButton,daemon=True)
#t.run()
clickButton()
while():
    continue
    
#python gamepad.py