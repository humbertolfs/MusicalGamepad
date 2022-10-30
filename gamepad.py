from doctest import testfile
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
dictNotaBut ={}
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

def yesMapButton():
    global fineMapping
    lbl.configure(text="Mapeando Botoes... ")
    btnYesMap.destroy()
    btnNoMap.destroy()
    fineMapping = "s"
def noMapButton():
    lbl.configure(text="Mapeando Botoes... ")
    global fineMapping
    btnYesMap.destroy()
    btnNoMap.destroy()
    fineMapping = "n"    

def editarBotao(threadName, id):
    global btnNoMap
    global btnYesMap
    global fineMapping
    global stillplayingInstrument
    global thisdict
    global dictNotaBut
    button = botao[id]
    fineMapping = "?"
    while(fineMapping=="?"):
        labelMiddle.configure(text="Defina uma nota para o botao: "+str(button))
        time.sleep(1)
        nota = getNote()
        labelMiddle.configure(text="Esta eh a nota que voce quer,  "+ str(nota) +" para o Botao "+ str(button)+  " ?")   
        btnYesMap = Button(top, text="Sim", command=yesMapButton)
        btnYesMap.grid(column=0, row=3)
        btnNoMap = Button(top, text="Nao", command=noMapButton)
        btnNoMap.grid(column=1, row=3)

        while(fineMapping=="?"):
            #SE NAO COLOCAR TIMER, COME MUITO PROCESSAMENTO
            #O IDEAL SERIA USAR UM CANAL DE GOLANG
            time.sleep(1)
        if (fineMapping == "n"):
            fineMapping = "?"
        
        #TROCA OS BOTOES (SE CIMA EH A~ E BAIXO EH B~ E EU QUERO Q CIMA SEJA B=>)
        #ENTAO EU FACO CIMA SER B~ E MUDO BAIXO PRA A~
        thisdict[list(dictNotaBut.keys())[list(dictNotaBut.values()).index(button)]] = thisdict[nota]
        thisdict[nota] = vgButton(button)
        #print("a",thisdict)
        dictNotaBut[list(dictNotaBut.keys())[list(dictNotaBut.values()).index(button)]] = dictNotaBut[nota]
        dictNotaBut[nota]=button
        #print("b",dictNotaBut)
    stillplayingInstrument = "s"
    top.destroy()


def editarBotaoThread(id):
    global top
    global labelTop
    global labelMiddle
    
    #destroy all buttons
    for i in lblArray:
        i.destroy()
    
    for i in lblButtonArray:
        i.destroy()
    endBtn.destroy()

    top= Toplevel(window)
    top.title("Editing a single button")
    labelTop = Label(top, text= "editing...!")
    labelTop.grid(column=0, row=1)
    labelMiddle = Label(top, text= " ")
    labelMiddle.grid(column=0, row=2)

    t = Thread(target=editarBotao,args =("editarBotao",id))
    t.start()
       
#atual
def fimDaEdicao():
    global stillplayingInstrument
    global stillEditing
    
    stillEditing = "n"
    stillplayingInstrument ="s"
def limpaGui():
    for i in lblArray:
        i.destroy()
    
    for i in lblButtonArray:
        i.destroy()
    endBtn.destroy()
    a= Label(window, text="Running gamepad") 
    a.grid(column=0, row=1)
                
def interfaceMultiOptionTk(agreeMap):
    global lblArray
    global lblButtonArray
    global endBtn
    global stillplayingInstrument
    global stillEditing

    stillEditing ="s"
    lblArray = []
    lblButtonArray =[]
    for i in range(12):
        thisdict[notas[i]] = vgButton(botao[i])
        dictNotaBut[notas[i]]=botao[i]
    if(agreeMap=="s"):
        #loop acontece enquanto voce esta editando notas
        while(stillEditing=="s"):
            lblArray = []
            lblButtonArray =[]
            stillplayingInstrument = "n"
            for i in range(12):
                #accessing key dictionary by value (inverse dict acess)
                lblArray.append(Label(window, text="botao: "+ str(botao[i]) + " = nota: "+list(dictNotaBut.keys())[list(dictNotaBut.values()).index(botao[i])])) 

                lblArray[i].grid(column=0, row=i+2)
                lblButtonArray.append(Button(window, text="Editar", command = lambda c=i : editarBotaoThread(c)))
                lblButtonArray[i].grid(column=1, row=i+2)
                endBtn = Button(window, text="Fim de edicao", command =fimDaEdicao)
                endBtn.grid(column=1, row=14)
            
            while(stillplayingInstrument=="n"):
                #SE NAO COLOCAR TIMER, COME MUITO PROCESSAMENTO
                #O IDEAL SERIA USAR UM CANAL DE GOLANG
                time.sleep(1)
    #limpaGui()
    t = Thread(target =clickButton,args =())
    t.start()

    window.destroy()
    #clickButton()


def yesClick():
    global lbl1
    lbl.configure(text="Mapeando Botoes: ")
    btnYes.destroy()
    btnNo.destroy()
    lbl1 = Label(window, text="starting")
    lbl1.grid(column=0, row=2)
    #window.destroy()
    t = Thread(target =interfaceMultiOptionTk,args =("s"))
    #t = Thread(target =interfaceButtonMapTkinter,args =("s"))
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



