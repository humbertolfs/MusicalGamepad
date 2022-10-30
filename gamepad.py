from doctest import testfile
import os
import configparser
from tabnanny import check
import vgamepad as vg
import time
import PySimpleGUI as sg
from threading import Thread
from tuner_audio.audio_analyzer import AudioAnalyzer
from tuner_audio.threading_helper import ProtectedList
from tkinter import *

DEFAULT_BUFFER_SIZE = 8
DEFAULT_MINIMUM_VOLUME = 800
DEFAULT_NOTE_LEEWAY = 6

config = configparser.ConfigParser() #Criação do arquivo de config

def checkConfig():
    if not os.path.isfile('gamepadconfig.ini'): 
        with open('gamepadconfig.ini', 'w') as configfile:
            config['BOTOES'] = {
                "cima": "A",
                "baixo": "A#",
                "esquerda": "B",
                "direita": "C",
                "A": "C#",
                "B": "D",
                "X": "D#",
                "Y": "E",
                "Lb": "F",
                "Lt": "F#",
                "Rb": "G",
                "Rt": "G#"
            }
            config['OPTIONS'] = {
                "buffersize": str(DEFAULT_BUFFER_SIZE),
                "minimumvolume": str(DEFAULT_MINIMUM_VOLUME),
                "noteleeway": str(DEFAULT_NOTE_LEEWAY)
            }
            config.write(configfile)
    config.read('gamepadconfig.ini')

def rewriteConfigBotoes(button1, button2, note1, note2):
    checkConfig()
    with open('gamepadconfig.ini', 'w') as configfile:
        config['BOTOES'][button1] = note1
        config['BOTOES'][button2] = note2
        config.write(configfile)

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

def readConfigFileNotas():
    notas = []
    for botao in config['BOTOES']:  
        notas.append(config['BOTOES'][botao])
    return notas

thisdict = {}
dictNotaBut = {}

botoes = ["cima", "baixo", "esquerda", "direita", "A", "B", "X", "Y", "Lb", "Lt", "Rb", "Rt"]
checkConfig()
notas = readConfigFileNotas()
window = Tk()
bufferSizeVariable = StringVar(window, config['OPTIONS']['buffersize'])
minimumVolumeVariable = StringVar(window, config['OPTIONS']['minimumvolume'])
noteLeewayVariable = StringVar(window, config['OPTIONS']['noteleeway'])

noteLeeway = int(noteLeewayVariable.get())

for i in range(12):
    thisdict[notas[i]] = vgButton(botoes[i])
    dictNotaBut[notas[i]] = botoes[i]
frequency_queue = ProtectedList(buffer_size = int(bufferSizeVariable.get()))
agree = "?"
audio_analyzer = AudioAnalyzer(frequency_queue, minimum_volume = int(minimumVolumeVariable.get())) #Pode-se mudar o volume mínimo usando set_minimum_volume
#esse start nao deixa dar o ctrl + c keyboard interrupt
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
        gamepad.left_trigger(value = 255)
    elif thisdict[note] == "Rt":
        gamepad.right_trigger(value = 255)
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

def getFreq():
    freq = frequency_queue.get()    
    if freq is not None:
        # convert frequency to note number
        number = audio_analyzer.frequency_to_number(freq, a4_frequency)

        # calculate nearest note number, name and frequency
        nearest_note_number = round(number)

        note = audio_analyzer.number_to_note_name(nearest_note_number)
    else:
        note = None

    if len(frequency_queue.elements) >= len(frequency_queue.elements):
        if frequency_queue.elements[len(frequency_queue.elements) - 1] == None:
            note = None
    return note

def getNote():
    note = None
    while (note == None):
        note = getFreq()
        if(note != None):
            return note
        time.sleep(0.033) #30FPS
        
def clickButton():
    global noteLeeway
    global clickButtonThreadRunningCheck
    clickButtonThreadRunningCheck = True
    lastNote = None
    lastNotes = ProtectedList(buffer_size = noteLeeway)
    print("Audio Analizer Awaiting first value...")
    while (not audio_analyzer.running or frequency_queue.get() is None) and not editingThreadRunningCheck: #Só irá iniciar quando o volume mínimo for atingido
        time.sleep(0.5)
    print("Audio Analizer Running")

    while (audio_analyzer.running):
        if not editingThreadRunningCheck:
            note = getFreq()

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
                if len(lastNotes.elements) >= noteLeeway:
                    lastValid = True
                    for i in range(noteLeeway):
                        if lastNotes.elements[i] != note:
                            lastValid = False
                    if lastValid == True:
                        lastNote = note
                        buttonPress(note)
            
        time.sleep(0.033) #30FPS

def yesMapButton():
    global fineMapping
    lbl.configure(text = "Mapeando Botoes... ")
    btnYesMap.destroy()
    btnNoMap.destroy()
    fineMapping = "s"

def noMapButton():
    lbl.configure(text = "Mapeando Botoes... ")
    global fineMapping
    btnYesMap.destroy()
    btnNoMap.destroy()
    fineMapping = "n"    

def editarBotao(editarBotaoThreadName, id):
    global btnNoMap
    global btnYesMap
    global fineMapping
    global stillplayingInstrument
    global thisdict
    global dictNotaBut
    global editingThreadRunningCheck
    editingThreadRunningCheck = True

    button = botoes[id]
    fineMapping = "?"
    while(fineMapping == "?"):
        labelMiddle.configure(text = "Defina uma nota para o botão: " + str(button))
        time.sleep(1)
        nota = getNote()
        labelMiddle.configure(text = "Você quer a nota " + str(nota) + " para o botão " + str(button) + "?")   
        btnYesMap = Button(top, text = "Sim", command = yesMapButton)
        btnYesMap.grid(column = 0, row = 3)
        btnNoMap = Button(top, text = "Não", command = noMapButton)
        btnNoMap.grid(column = 1, row = 3)

        while(fineMapping == "?"):
            #SE NAO COLOCAR TIMER, COME MUITO PROCESSAMENTO
            #O IDEAL SERIA USAR UM CANAL DE GOLANG
            time.sleep(0.5)
        if (fineMapping == "n"):
            fineMapping = "?"
        
        #TROCA OS BOTOES (SE CIMA EH A~ E BAIXO EH B~ E EU QUERO Q CIMA SEJA B=>)
        #ENTAO EU FACO CIMA SER B~ E MUDO BAIXO PRA A~
        if fineMapping == "s":
            thisdict[list(dictNotaBut.keys())[list(dictNotaBut.values()).index(button)]] = thisdict[nota]
            thisdict[nota] = vgButton(button)
            checkConfig()
            rewriteConfigBotoes(dictNotaBut[nota], button, config['BOTOES'][button], nota)

            dictNotaBut[list(dictNotaBut.keys())[list(dictNotaBut.values()).index(button)]] = dictNotaBut[nota]
            dictNotaBut[nota] = button

    nota = None
    stillplayingInstrument = "s"
    editingThreadRunningCheck = False
    top.destroy()

def closedEdit():
    global stillplayingInstrument
    global fineMapping
    stillplayingInstrument = "s"
    fineMapping = "s"
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
    endBtn.grid_forget()

    top = Toplevel(window)
    top.title("Editing a single button")
    top.protocol("WM_DELETE_WINDOW", closedEdit)
    labelTop = Label(top, text = "Editing...")
    labelTop.grid(column = 0, row = 1)
    labelMiddle = Label(top, text= " ")
    labelMiddle.grid(column = 0, row = 2)

    t = Thread(target = editarBotao, args = ("editarBotaoThreadName", id))
    t.start()
       
#atual
def fimDaEdicao():
    global stillplayingInstrument
    global stillEditing
    
    stillEditing = "n"
    stillplayingInstrument ="s"

def limpaGui(agreeMap):
    global lbl
    for i in lblArray:
        i.destroy()
    
    for i in lblButtonArray:
        i.destroy()
    if agreeMap == 's':
        endBtn.grid_forget()
    window.update()
    lbl.config(text = "           Running gamepad...           ")
                
def interfaceMultiOptionTk(agreeMap):
    global lblArray
    global lblButtonArray
    global endBtn
    global stillplayingInstrument
    global stillEditing

    stillEditing ="s"
    lblArray = []
    lblButtonArray =[]
    if(agreeMap == "s"):
        #loop acontece enquanto voce esta editando notas
        while(stillEditing == "s"):
            lblArray = []
            lblButtonArray =[]
            stillplayingInstrument = "n"
            for i in range(12):
                #accessing key dictionary by value (inverse dict acess)
                lblArray.append(Label(window, text = "Botão: "+ str(botoes[i]) + " = Nota: "+ list(dictNotaBut.keys())[list(dictNotaBut.values()).index(botoes[i])])) 

                lblArray[i].grid(column = 0, row = i+2)
                lblButtonArray.append(Button(window, text = "Editar", command = lambda c=i : editarBotaoThread(c)))
                lblButtonArray[i].grid(column = 1, row = i+2)
                endBtn.grid(column = 1, row = 14)
            
            while(stillplayingInstrument == "n"):
                #SE NAO COLOCAR TIMER, COME MUITO PROCESSAMENTO
                #O IDEAL SERIA USAR UM CANAL DE GOLANG
                time.sleep(0.5)
    limpaGui(agreeMap)
    mainGui()
    if clickButtonThreadRunningCheck == False:
        t = Thread(target = clickButton, args = ())
        t.start()

def setOptions(a):
    global bufferSizeVariable
    global minimumVolumeVariable
    global noteLeewayVariable
    global noteLeeway

    if int(bufferSizeVariable.get()) < 2:
        bufferSizeVariable.set("2")
    if int(bufferSizeVariable.get()) > 128:
        bufferSizeVariable.set("128")
    
    if int(minimumVolumeVariable.get()) < 0:
        minimumVolumeVariable.set("0")
    if int(minimumVolumeVariable.get()) > 5000:
        minimumVolumeVariable.set("5000")
    
    if int(noteLeewayVariable.get()) < 1:
        minimumVolumeVariable.set("1")
    if int(noteLeewayVariable.get()) > 20:
        minimumVolumeVariable.set("20")
    
    frequency_queue.buffer_size = int(bufferSizeVariable.get())
    audio_analyzer.minimum_volume = int(minimumVolumeVariable.get())
    noteLeeway = int(noteLeewayVariable.get())

    checkConfig()
    with open('gamepadconfig.ini', 'w') as configfile:
        config['OPTIONS']['buffersize'] = bufferSizeVariable.get()
        config['OPTIONS']['minimumvolume'] = minimumVolumeVariable.get()
        config['OPTIONS']['noteleeway'] = noteLeewayVariable.get()
        config.write(configfile)

    print("Values updated!")

def mainGui():
    global btnEdit
    global entryBuffer
    global entryVolume
    global entryLeeway
    btnEdit.grid(column = 0, row = 2)
    entryBuffer.grid(column = 0, row = 3)
    entryVolume.grid(column = 0, row = 4)
    entryLeeway.grid(column = 0, row = 5)

def editClick():
    global maingui
    global btnEdit
    global entryBuffer
    global entryVolume
    global entryLeeway
    maingui = False
    lbl.configure(text = "Mapeando Botoes: ")
    btnEdit.grid_forget()
    entryBuffer.grid_forget()
    entryVolume.grid_forget()
    entryLeeway.grid_forget()
    t = Thread(target = interfaceMultiOptionTk, args = ("s"), daemon = True)
    t.start()
    

def yesClick():
    lbl.configure(text = "Mapeando Botoes: ")
    btnYes.destroy()
    btnNo.destroy()
    t = Thread(target = interfaceMultiOptionTk, args = ("s"), daemon = True)
    t.start()

def noClick():
    btnYes.destroy()
    btnNo.destroy()
    lbl.configure(text = "Botões configurados automaticamente!!")
    window.update()
    time.sleep(1)
    t = Thread(target = interfaceMultiOptionTk, args = ("n"), daemon = True)
    t.start()

def closeClick():
    btnYes.destroy()
    btnNo.destroy()
    window.destroy()
    os._exit(0)

def guiInterface():
    global clickButtonThreadRunningCheck
    global editingThreadRunningCheck
    global btnYes
    global btnNo
    global lbl
    global endBtn

    global btnEdit
    global entryBuffer
    global entryVolume
    global entryLeeway

    clickButtonThreadRunningCheck = False
    editingThreadRunningCheck = False

    window.protocol("WM_DELETE_WINDOW", closeClick)
    window.title("Musical Gamepad")

    #window.geometry(str(column)+"x"+str(row))

    lbl = Label(window, text = "Você quer mapear os botoes?")
    lbl.grid(column = 0, row = 1)

    btnYes = Button(window, text = "Sim", command = yesClick)
    btnYes.grid(column = 0, row = 2)

    btnNo = Button(window, text = "Não", command = noClick)
    btnNo.grid(column = 1, row = 2)

    endBtn = Button(window, text = "Fim de Edição", command = fimDaEdicao)

    btnEdit = Button(window, text = "Editar Botões", command = editClick)
    entryBuffer = Entry(window, textvariable = bufferSizeVariable)
    entryBuffer.bind('<Return>', setOptions)
    entryVolume = Entry(window, textvariable = minimumVolumeVariable)
    entryVolume.bind('<Return>', setOptions)
    entryLeeway = Entry(window, textvariable = noteLeewayVariable)
    entryLeeway.bind('<Return>', setOptions)

    window.mainloop()

#Main:
guiInterface()



