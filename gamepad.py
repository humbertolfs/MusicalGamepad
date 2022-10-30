import vgamepad as vg
import time
import PySimpleGUI as sg
from threading import Thread
from tuner_audio.audio_analyzer import AudioAnalyzer
from tuner_audio.threading_helper import ProtectedList
from tkinter import *

BUFFER_SIZE = 8
MINIMUM_VOLUME = 800
NOTE_LEEWAY = 6

thisdict = {}
botao = ["cima","baixo","esquerda","direita","A","B","X","Y","Lb","Lt","Rb","Rt"]
notas = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
frequency_queue = ProtectedList(buffer_size = BUFFER_SIZE)
agree = "?"
audio_analyzer = AudioAnalyzer(frequency_queue, minimum_volume = MINIMUM_VOLUME) #Pode-se mudar o volume mínimo usando set_minimum_volume
#esse start nao deixa dar o ctrl + c
audio_analyzer.start()

nearest_note_number_buffered = 69
a4_frequency = 440

gamepad = vg.VX360Gamepad()

# pressing a button to wake the device up
gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
gamepad.update()

gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
gamepad.update()
time.sleep(0.5)


print("Audio Analizer Started")
note = None

def buttonPress(note):
    if thisdict[note] == "Lt":
        gamepad.left_trigger(value=255)
    elif thisdict[note] == "Rt":
        gamepad.right_trigger(value=255)
    else:
        gamepad.press_button(thisdict[note])
    gamepad.update()


def buttonRelease(note):
    if thisdict[note] == "Lt":
        gamepad.left_trigger(value=0)
    elif thisdict[note] == "Rt":
        gamepad.right_trigger(value=0)
    else:
        gamepad.release_button(thisdict[note])
    gamepad.update()

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
            return "Lt"
        case "Rb":
            return vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER
        case "Rt":#a
            return "Rt"


def getNote():
    note = None
    while (note == None):
        freq = frequency_queue.get()    
        if freq is not None:
            # convert frequency to note number
            number = audio_analyzer.frequency_to_number(freq, a4_frequency)

            # calculate nearest note number, name and frequency
            nearest_note_number = round(number)

            note = audio_analyzer.number_to_note_name(nearest_note_number)
        else:
            note = None
        if len(frequency_queue.elements) >= BUFFER_SIZE:
            if frequency_queue.elements[len(frequency_queue.elements) - 1] == None:
                note = None
        if(note!=None):
            #print(note)
            return note
        time.sleep(0.033) #30FPS
        
def clickButton():
    lastNote = None
    lastNotes = ProtectedList(buffer_size = NOTE_LEEWAY)
    print("Audio Analizer Awaiting first value...")
    while (not audio_analyzer.running or frequency_queue.get() is None): #Só irá iniciar quando o volume mínimo for atingido
        time.sleep(0.5)
    print("Audio Analizer Running")

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

        lastNotes.put(note)
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
        
        if note == None and lastNote != None: #Atualmente, se você tocar mais de uma nota sem deixar silêncio entre elas, você pode apertar mais de um botão.
            buttonRelease(lastNote)
            for i in notas:
                buttonRelease(i)
        elif note != None:
            if len(lastNotes.elements) >= NOTE_LEEWAY:
                lastValid = True
                for i in range(NOTE_LEEWAY):
                    if lastNotes.elements[i] != note:
                        lastValid = False
                if lastValid == True:
                    lastNote = note
                    buttonPress(note)
        
        time.sleep(0.033) #30FPS

 
def interfaceButtonMap():
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




def interfaceButtonMapTkinter(agreeMap):
    def yesNoteClick():
        global agree
        lbl.configure(text="Mapeando Botoes... ")
        btnYesCadastro.destroy()
        btnNoCadastro.destroy()
        agree = "s"
    
    def noNoteClick():
        global agree
        lbl.configure(text="Mapeando Botoes... ")
        btnYesCadastro.destroy()
        btnNoCadastro.destroy()
        agree = "n"
    
    global agree
    global lb1

    print("Voce quer mapear os botoes?(s/n)")
    #agreeMap = input()
    for i in range(12):
            thisdict[notas[i]] = vgButton(botao[i])
    if(agreeMap != "n"):
        for button in botao:
            agree = "?"
            while(agree=="?"):
                #print("Defina uma nota para o botao: ", button)
                lbl1.configure(text="Defina uma nota para o botao: "+str(button))
                time.sleep(1)
                nota = getNote()
                #print("Esta eh a nota que voce quer, ", nota ,"para o botao",button, " ? (s/n)")
                lbl1.configure(text="Esta eh a nota que voce quer,  "+ str(nota) +" para o Botao "+ str(button)+  " ?")
                btnYesCadastro = Button(window, text="Sim", command=yesNoteClick)
                btnYesCadastro.grid(column=0, row=3)
                btnNoCadastro = Button(window, text="Nao", command=noNoteClick)
                btnNoCadastro.grid(column=1, row=3)
                #print (nota)
                #print(agree)
                while(agree=="?"):
                    pass
                if (agree == "n"):
                    agree = "?"
                
                #print("Esta eh a nota que voce quer, ", nota ,"para o botao",button, " ? (s/n)")
                #agree = input()
            thisdict[nota] = vgButton(button)
    #window.destroy()
    clickButton()

def yesClick():
    global lbl1
    lbl.configure(text="Mapeando Botoes: ")
    btnYes.destroy()
    btnNo.destroy()
    lbl1 = Label(window, text="starting")
    lbl1.grid(column=0, row=2)
    #window.destroy()
    #t = Thread(target =interfaceMultiOptionTk,args =("s"))
    t = Thread(target =interfaceButtonMapTkinter,args =("s"))
    t.start()

def noClick():
    btnYes.destroy()
    btnNo.destroy()
    lbl.configure(text="Botoes configurados automaticamente!!")
    t = Thread(target =interfaceButtonMapTkinter,args =("n"))
    t.start()
    #interfaceButtonMapTkinter("n")
    

def guiInterface():
    global btnYes
    global btnNo
    global lbl
    global window
    column = 300
    row = 150
    window = Tk()

    window.title("Musical Gamepad")

    #window.geometry(str(column)+"x"+str(row))

    lbl = Label(window, text="Voce quer mapear os botoes?")
    lbl.grid(column=0, row=1)

    btnYes = Button(window, text="Sim", command=yesClick)
    btnYes.grid(column=0, row=2)

    btnNo = Button(window, text="Nao", command=noClick)
    btnNo.grid(column=1, row=2)

    window.mainloop()

guiInterface()
#interfaceButtonMap()
#clickButton()



