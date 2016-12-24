############# CADENZA ###################
##### Wynne Yao 15-112 Term Project #####
#########################################

import pyaudio
import wave
from array import array
from struct import pack
from PIL import ImageTk, Image 
import PIL.Image
import os
import random 
from pydub import AudioSegment
from pydub.playback import play 
from tkinter import messagebox
from tkinter import simpledialog 
import copy 

#########################################
# Pydub Reference Section Taken from Tara Stentz's Audio Lecture

def soundFromFile(file):
    return AudioSegment.from_wav(file)

def getLen(file):
    return len(soundFromFile(file))

def changeVolume(file, amount):
    sound = soundFromFile(file)
    loudSound = sound + amount
    exportToFile(loudSound, "loudSound.wav")
    return "loudSound.wav"

def exportToFile(sound, file):
    sound.export(file, format="wav")
    return file

def concatNotes(sound1, sound2, filename):
    return exportToFile(sound1 + sound2, filename)

def repeatSound(file, amount):
    sound = soundFromFile(file)
    return exportToFile(sound * amount, "repeat.wav")

def getSection(file, start, end):
    start *= 1000
    end *= 1000
    sound = soundFromFile(file)
    newSound = sound[start:end]
    return exportToFile(newSound, "slice.wav")

# End Pydub Reference Section
##########################################

from tkinter import * 

def init(data):
    data.trebleNotes = []
    data.mode = 'splashScreen'
    data.prevMode = None
    data.scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    data.notesPositions = []
    data.notesY = []
    data.notesX = []
    data.topLines = []
    data.chords = []
    data.dottedQuarterNote = 375 #milliseconds 
    data.eighthNote = 125 
    data.quarterNote = 250 
    data.halfNote = 500
    data.timeSig = None
    data.keySig = None
    data.beatsPerMeasure = None
    data.measures = 5 
    data.difficultyLevel = 1 
    data.song = []
    data.notes = []
    data.missingChords = []
    data.notesOfMissingChords = []
    data.score = 0 
    data.drawingC = False 
    data.drawingCPrevMode = False
    data.notesWithMissingChords = []
    data.jazzMode = False
    data.jazzPrevMode = False 
    data.isCreatingNotes = False
    data.isCreatingNotesPrev = False 
    data.inversion = None 
    data.currRhythm = None
    data.pastRhythm = None
    data.missingChords1dList = []
    data.numMissingChords = 1
    data.solved = False
    data.printingSong = False
    data.validKeySigs = {'C major', 'A minor', 'G major', 'E minor', 
    	'D major', 'B minor', 'A major', 'F# minor', 'E major', 'C# minor', 
    	'B major', 'G# minor', 'F# major', 'D# minor', 'C# major', 'A# minor', 
    	'F major', 'D minor', 'Bb major', 'G minor', 'Eb major', 'C minor', 
    	'Ab major', 'F minor', 'Db major', 'Bb minor', 'Gb major', 
    	'Eb minor', 'Cb major', 'Ab minor'}

class Button(object): 
    textMargin = 5
    def __init__(self, buttonWidth, buttonHeight, x, y, text, 
        textSize=15, textColor="gray5", boxColor='light grey'):
        self.width = buttonWidth
        self.height = buttonHeight
        self.text = text
        self.textSize = textSize 
        self.x = x
        self.y = y
        self.textColor = textColor
        self.boxColor = boxColor
    def draw(self, canvas, data): 
        if (data.mode == 'cadence'): 
            canvas.create_rectangle(self.x, self.y, 
                            self.x+self.width, 
                            self.y+self.height, 
                            fill = self.boxColor)
        canvas.create_text(self.x+self.width//2, 
                        self.y+self.height//2,
                        text = self.text, 
                        font = "Helvetica "+str(self.textSize), 
                        fill = self.textColor)

def makeJazzBeat(data): 
    jazzPattern1 = [data.dottedQuarterNote, data.eighthNote, data.quarterNote, 
    	data.quarterNote]
    jazzPattern2 = [data.eighthNote, data.dottedQuarterNote, data.eighthNote, 
    	data.dottedQuarterNote]
    jazzPattern3 = [data.dottedQuarterNote, data.dottedQuarterNote, 
    	data.eighthNote, data.eighthNote]
    jazzPattern4 = [data.dottedQuarterNote, data.eighthNote, 
    	data.dottedQuarterNote, data.eighthNote] 
    jazzPattern5 = [data.dottedQuarterNote, data.eighthNote, 
    	data.dottedQuarterNote, data.eighthNote]
    jazzBeats = [jazzPattern1, jazzPattern2, 
        jazzPattern3, jazzPattern4, jazzPattern5]
    # change this to a markov chain that ends when run out of the number of 
    # notes
    while(data.currRhythm == None or data.currRhythm == data.pastRhythm):
        baseRhythm = random.choice(jazzBeats) 
        data.currRhythm = baseRhythm 
        #keep choosing until you get one different from last
        #choose the rhythm off of which to make variations
    data.pastRhythm = baseRhythm
    measuresPerLine = 5
    fullRhythm = baseRhythm*measuresPerLine
    chordList = []
    for chord in data.chords:
        chordList += [changeChordStringToList(chord)] 
        #chordList in form [['C', 'E', 'G'], ['F', 'A', 'C']]
        #data.chords is in form ['CEG', 'FAC'...]
    indicesOfThree = divideByThree(data.missingChords)
    for i in range(len(fullRhythm)): 
        if (i in indicesOfThree and data.solved == False): 
            silence = AudioSegment.from_wav(
                "Media/Piano/silence4.wav")
            play(silence)
        else: 
            note1 = AudioSegment.from_wav(
                "Media/Saxophone/"+chordList[i][0]+"3.wav"
                )[:fullRhythm[i]]
            note2 = AudioSegment.from_wav(
                "Media/Saxophone/"+chordList[i][1]+"3.wav"
                )[:fullRhythm[i]]
            note3 = AudioSegment.from_wav(
                "Media/Saxophone/"+chordList[i][2]+"3.wav"
                )[:fullRhythm[i]]
            chordTriad = note1.overlay(note2)
            chordFull = chordTriad.overlay(note3)
            play(chordFull)

def createBeat(data): 
	if (data.genre == "Jazz"):
		makeJazzBeat(data)

def mousePressed(event, data): 
    if (data.mode == "splashScreen"): splashScreenMousePressed(event, data)
    elif (data.mode == "cadence"): cadenceMousePressed(event, data) 
    elif (data.mode == "difficulty"): difficultyLevelMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    elif (data.mode == "cadence"): cadenceKeyPressed(event, data)
    elif (data.mode == "difficulty"): difficultyLevelKeyPressed(event, data)
    elif(data.mode == "helpScreen"): helpScreenKeyPressed(event, data)
    elif (data.mode == "cadenceRef"): cadenceRefKeyPressed(event, data)
    elif (data.mode == 'success'): successKeyPressed(event, data)

def timerFired(data): 
	if (data.mode == "splashScreen"): splashScreenTimerFired(data)
	elif (data.mode == "cadence"): cadenceTimerFired(data) 
	elif (data.mode == "difficulty"): difficultyLevelTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    elif (data.mode == "cadence"): cadenceRedrawAll(canvas, data) 
    elif (data.mode == "difficulty"): difficultyLevelRedrawALl(canvas, data)
    elif (data.mode == "success"): successRedrawAll(canvas, data)
    elif (data.mode == 'helpScreen'): helpScreenRedrawAll(canvas, data)
    elif (data.mode == 'cadenceRef'): cadenceRefRedrawAll(canvas, data)

##############################
# splashScreen mode
##############################

def splashScreenMousePressed(event, data):
    # use event.x and event.y
    widthPlay = 90
    widthHow = 210
    widthCadences = 170
    height = 50
    margin = 70  
    xPlay = data.width//2-widthPlay//2
    xHelp = data.width//2-widthHow//2
    xCadences = data.width//2-widthCadences//2
    yPlay = data.height//2+margin
    yHelp = data.height//2+margin*2
    yCadences = data.height//2+margin*3
    if  (xPlay < event.x < xPlay+widthPlay and 
        yPlay < event.y < yPlay+height): 
        data.mode = 'difficulty'
        data.prevMode = 'splashScreen'
    elif (xHelp< event.x < xHelp+widthHow  and 
        yHelp < event.y < yHelp+height): 
        data.mode = 'helpScreen'
        data.prevMode = 'splashScreen'
    elif (xCadences < event.x < xCadences+widthCadences and
        yCadences < event.y < yCadences+height): 
        data.mode = 'cadenceRef'
        data.prevMode = 'splashScreen'

def splashScreenKeyPressed(event, data): 
    pass 

def splashScreenTimerFired(data): 
    pass

def drawTitle(canvas, data): 
    width = data.width//2
    height = data.height//3
    margin = 10 
    dFromTop = 100
    canvas.create_text(data.width//2, data.height//2-dFromTop, 
                        text = "CADENZA", font = "Helvetica 75 bold", 
                        fill = "white")
                        
def splashScreenRedrawAll(canvas, data): 
    drawImage(canvas, "Media/ending.jpg", 
            data.width, data.height, data.width//2, data.height//2)
    drawTitle(canvas, data)
    widthPlay = 90
    widthHow = 210
    widthCadences = 170
    height = 50
    margin = 70  
    xPlay = data.width//2-widthPlay//2
    xHelp = data.width//2-widthHow//2
    xCadences = data.width//2-widthCadences//2
    yPlay = data.height//2+margin
    yHelp = data.height//2+margin*2
    yCadences = data.height//2+margin*3
    textSize = 35
    Button(widthPlay, height, xPlay, yPlay, 
        "Play!", textSize, 'white').draw(canvas, data)
    Button(widthHow, height, xHelp, yHelp, 
        "How To Play", textSize, 'white').draw(canvas, data)
    Button(widthCadences, height, 
        xCadences, yCadences, "Cadences", textSize, 
        'white').draw(canvas, data)

###########################################
# helpScreen Mode
###########################################

def helpScreenKeyPressed(event, data): 
    if (event.keysym == 'm'): 
        data.mode = "splashScreen"
        data.prevMode = "helpScreen"
    elif (event.keysym == 'r' and data.prevMode == 'cadence'): 
        data.mode = 'cadence'
        data.prevMode = 'helpScreen'

def helpScreenRedrawAll(canvas, data): 
    addedWidth = 350
    addedHeight = 250
    drawImage(canvas, "Media/musicnotebg.jpg", 
            data.width, data.height, data.width//2, data.height//2)
    drawImage(canvas, "Media/helpscreenbg.jpg", 
            data.width//2+addedWidth, data.height//2+addedHeight, 
            data.width//2, data.height//2)
    marginFromTop = 55
    canvas.create_text(data.width//2, marginFromTop, text = "HOW TO PLAY",
        font = "Helvetica 50 bold", fill = "white")
    startMargin = data.width//7
    margin = 30 
    xHelp = data.width//8
    canvas.create_text(xHelp, startMargin, anchor = NW,
        text = "1. Enter a key and time signature."
        "\n2. Click 'Make Song' and fill in the missing chords using"
        "\n progressions."
        "\nIf you need a hint, press 'Play' to hear the song."
        "\n3. To fill in the missing chords, press the key 'n' and click"
        "\nwhere you want the note."
        "\n4. For the beginner level, if you accidentally create an inversion,"
        "\nit's still counted as correct. For advanced, you must be"  
        "\ncompletely correct."
        "\n\n     Cadence guidelines: In music, there are progressions" 
        "\n     - chords change to other chords."
        "\n     Go to 'Cadence' for more."
        "\n\n5. Just for fun, you can 'Jazzify' the song!"
        "\n\nPress 'm' for Main Menu and 'r' to return to the game.", 
        font = "Helvetica 20") 

###########################################
# cadenceRef Mode 
###########################################
def cadenceRefKeyPressed(event, data): 
    if (event.keysym == 'r' and data.prevMode == 'cadence'): 
        data.mode = 'cadence'
        data.prevMode = 'cadenceRef'
    elif (event.keysym == 'm'): 
        data.mode = 'splashScreen'
        data.prevMode = 'cadenceRef'

def cadenceRefRedrawAll(canvas, data): 
    addedWidth = 300
    addedHeight = 200
    drawImage(canvas, "Media/musicnotebg.jpg", 
            data.width, data.height, data.width//2, data.height//2)
    drawImage(canvas, "Media/helpscreenbg.jpg", 
            data.width//2+addedWidth, data.height//2+addedHeight, 
            data.width//2, data.height//2) 
    marginFromTop = data.height//10
    canvas.create_text(data.width//2, marginFromTop, text = "CADENCE REFERENCE",
        font = "Helvetica 40 bold", fill = "white")
    startMargin = data.width//6
    margin = 30 
    xInstructions = data.width//8
    canvas.create_text(xInstructions, startMargin, anchor = NW,
        text = "                                   Types of cadences:"
        "\n\n1. Perfect Cadence: V - I. Usually reserved for resolutions."
        "\n2. Plagal Cadence: IV - I. Usually used to add tension."
        "\n3. Imperfect Cadence: ? - V. Also used to add tension."
        "\n\n                                 Common progressions:"
        "\n                   (from most likely to least likely to occur):"
        "\n\n                                          I to IV, V"
        "\n                                          II to I, V"
        "\n                                          IV to I, V"
        "\n                                          V to I, IV, II"
        "\n\n   Press 'r' to return to the game and 'm' for Main Menu.",
        font = "Helvetica 20") 

###########################################
# Difficulty Mode 
###########################################

def difficultyLevelMousePressed(event, data): 
    widthButton = 300
    heightButton = 70
    xBeginner = xAdvanced = data.width//3.5
    yBeginner = data.height//2-50
    yAdvanced = data.height//2+50
    if (xBeginner < event.x < xBeginner+widthButton and
        yBeginner < event.y < yBeginner+heightButton): 
        data.difficultyLevel = 1
        data.mode = "cadence"
    elif (xAdvanced < event.x < xAdvanced+widthButton and
        yAdvanced < event.y < yAdvanced+heightButton): 
        data.difficultyLevel = 2
        data.mode = "cadence"

def difficultyLevelKeyPressed(event, data): 
	pass

def difficultyLevelTimerFired(data): 
	pass

def difficultyTitle(canvas, data): 
	margin = data.height//8
	canvas.create_text(data.width//2, margin, 
		text = "Choose Your Difficulty Level", font = "Helvetica 50",
		fill = "white")

def difficultyLevelRedrawALl(canvas, data): 
    widthButton = 300
    heightButton = 70
    xBeginner = xAdvanced = data.width//3.5
    yBeginner = data.height//2-70
    yAdvanced = data.height//2+70
    margin = 10 
    height = 3.5
    drawImage(canvas, "Media/ending.jpg", 
            data.width, data.height, data.width//2, data.height//2)
    Button(widthButton, heightButton, xBeginner, yBeginner, 
        "Beginner", 45, 'white').draw(canvas, data)
    Button(widthButton, heightButton, xAdvanced, yAdvanced,
        "Advanced", 45, 'white').draw(canvas, data)
    difficultyTitle(canvas, data)

##############################
# Cadence mode
##############################

def cadenceMousePressed(event, data): 
    xTime = xUndo = 70
    y = 50
    width = 150 
    height = 40 
    xKey = xDone = 230
    xSong = xIsDrawingC = 390
    xPlay = xJazz = 550
    xCheck = 50
    yCheck = data.height//2-50
    xScore = 50
    yScore = data.height//2
    xAnswer = 50
    yAnswer = data.height//2+50
    xNote = data.width-150
    yNote = data.height//2-10
    xDiff = xNote-width//2
    yDiff = yNote+35
    if (xTime < event.x < xTime+width and 
        y < event.y < y+height): 
        data.printingSong = False 
        getTime(data)
        validBeatsPerMeasure = [2, 4, 8]
        if (data.timeSig != None and int(data.timeSig[2]) not in 
            validBeatsPerMeasure): 
            messagebox.showinfo("CADENZA", "Make sure you have entered" 
                " a time signature with 2, 4, or 8 on the bottom!")
            getTime(data)
        try: 
            data.beatsPerMeasure = data.timeSig[0] 
            #timeSig is in form of 3/8 or 4/4 
        except: 
            messagebox.showinfo("CADENZA", "Make sure you have entered" 
                " a valid time signature!")
            getTime(data)
    elif (xKey < event.x < xKey+width and 
        y < event.y < y+height): 
        getKey(data)
        if (data.keySig not in data.validKeySigs): 
        	messagebox.showinfo("CADENZA", "Make sure you have entered" 
        		" a valid key signature!")
    elif (xSong < event.x < xSong+width and 
        y < event.y < y+height): 
        if (data.keySig == None or data.timeSig == None): 
            messagebox.showinfo("CADENZA", "Make sure you have entered" 
                " a key and time signature!")
        else: 
            if (data.song != []): 
                oldTimeSig = data.timeSig
                oldKeySig = data.keySig
                oldMode = data.mode 
                oldDiff = data.difficultyLevel
                oldBPM = data.beatsPerMeasure
                oldNumMissingChords = data.numMissingChords
                init(data)
                data.mode = oldMode
                data.timeSig = oldTimeSig
                data.beatsPerMeasure = oldBPM
                data.keySig = oldKeySig
                data.difficultyLevel = oldDiff
                data.numMissingChords = oldNumMissingChords
            data.printingSong = True 
            data.song = generateNewSong(data)
            transcribeSongToStaff(data)
            createListOfNotesOfMissingChords(data)
    elif (xPlay < event.x < xPlay+width and 
        y < event.y < y+height): 
        playSong(data)
    elif (xUndo < event.x < xUndo+width and 
        data.height-y < event.y < data.height-y+height):
        undo(data)
    elif (xDone < event.x < xDone+width and 
        data.height-y < event.y < data.height-y+height): 
        data.mode = 'success'
    elif (xIsDrawingC < event.x < xIsDrawingC+width and 
        data.height-y < event.y < data.height-y+height):
        if (data.drawingCPrevMode == False): 
            data.drawingC = True
            data.drawingCPrevMode = True
        else:
            data.drawingC = False #we were drawing C, so now stop drawing C  
            data.drawingCPrevMode = False 
    elif (xJazz < event.x < xJazz+width and 
        data.height-y < event.y < data.height-y+height): 
        if (data.jazzPrevMode == False): 
            data.jazzMode = True 
            data.jazzPrevMode = True  
        else: 
            data.jazzMode = False
            data.jazzPrevMode = False 
    elif (xCheck < event.x < xCheck+width and 
        yCheck < event.y < yCheck+height): 
        checkCorrect(data)
    elif (xDiff < event.x < xDiff+width and
        yDiff < event.y < yDiff+height): 
        getDiff(data)
    elif (xAnswer < event.x < xAnswer+width and 
        yAnswer < event.y < yAnswer+height):
        answer = "" 
        missingChords = makeIntoGroupsOfThreeWithAcc(data.notesOfMissingChords)
        for i in range(len(missingChords)):
                answer += "".join(missingChords[i])
                if (i != len(missingChords)-1): 
                    answer += ", " 
        messagebox.showinfo("CADENZA", "The answer is: "+str(answer))
    else: 
        xMargin = 50
        yMargin = 80
        lineHeight = 15
        staffHeight = 5*lineHeight+20 #add a margin for error 
        if (data.isCreatingNotes and 
            xMargin < event.x < data.width-xMargin
            and yMargin < event.y < yMargin+staffHeight+lineHeight): 
            data.notesPositions += [(event.x, event.y, data.drawingC)]
            data.notesY += [(event.y)]
            data.notesX += [(event.x)]
            detectTrebleNote(data)
    
def cadenceKeyPressed(event, data):
    if (event.keysym == "n"): 
        if (data.isCreatingNotesPrev == False): 
            data.isCreatingNotes = True 
            data.isCreatingNotesPrev = True 
        else: 
            data.isCreatingNotes = False 
            data.isCreatingNotesPrev = False  
    elif (event.keysym == 'h'): 
        data.mode = 'helpScreen'
        data.prevMode = 'cadence'
    elif (event.keysym == 'c'): 
        data.mode = 'cadenceRef'
        data.prevMode = 'cadence'
    elif (event.keysym == 'm'): 
        data.mode = 'splashScreen'
        data.prevMode = 'cadence'
    
def cadenceTimerFired(data):
    pass

############################
# For all modes
############################

def getKey(data): 
    root = Tk()
    data.keySig = simpledialog.askstring("Key","Enter key signature "
        "- ex. F# major, Bb minor, C major")

def getTime(data): 
    root = Tk()
    data.timeSig = simpledialog.askstring("Time Signature", 
        "Enter time signature"
        " - ex. 4/4, 3/8, 2/2")

def getDiff(data): 
    root = Tk()
    data.numMissingChords = int(simpledialog.askstring("Challenge", 
        "Enter how"
        " many chords you want to guess!"))

def keySignatures(key): 
    if (key == 'C major' or key == 'A minor'): 
        keysig = []
    elif (key == 'G major' or key == 'E minor'): #sharps 
        keysig = ['#', 'F'] 
    elif (key == 'D major' or key == 'B minor'):
        keysig = ['#', 'F', 'C']
    elif (key == 'A major' or key == 'F# minor'):
        keysig = ['#','F', 'C', 'G']
    elif (key == 'E major' or key == 'C# minor'):
        keysig = ['#','F', 'C', 'G', 'D']
    elif (key == 'B major' or key == 'G# minor'):
        keysig = ['#','F', 'C', 'G', 'D', 'A']
    elif (key == 'F# major' or key == 'D# minor'):
        keysig = ['#','F', 'C', 'G', 'D', 'A', 'E']
    elif (key == 'C# major' or key == 'A# minor'):
        keysig = ['#','F', 'C', 'G', 'D', 'A', 'E', 'B']
    elif (key == 'F major' or key == 'D minor'): #flats
        keysig = ['b','B']
    elif (key == 'Bb major' or key == 'G minor'):
        keysig = ['b','B', 'E']
    elif (key == 'Eb major' or key == 'C minor'):
        keysig = ['b','B', 'E', 'A']
    elif (key == 'Ab major' or key == 'F minor'):
        keysig = ['b','B', 'E', 'A', 'D']
    elif (key == 'Db major' or key == 'Bb minor'):
        keysig = ['b','B', 'E', 'A', 'D', 'G']
    elif (key == 'Gb major' or key == 'Eb minor'):
        keysig = ['b','B', 'E', 'A', 'D', 'G', 'C']
    elif (key == 'Cb major' or key == 'Ab minor'):
        keysig = ['b','B', 'E', 'A', 'D', 'G', 'C', 'F']
    try: 
    	return keysig 
    except: 
        messagebox.showinfo("Cadenza", 
            "Make sure you enter a valid key!")

def possibleChordsInKeySig(data, possibleChords): 
    #modifies possibleChords fcn with correct key signatures 
    keySigList = keySignatures(data.keySig) 
    chordsInKey = []
    realChord = ''
    for chord in possibleChords: 
        for note in chord:
            realChord += note
            if note in keySigList: 
                realChord += keySigList[0] #the sharp or the flat 
        chordsInKey += [realChord]
        realChord = ''
    return chordsInKey

def possibleChords(data):
	#gets the chord in I, II, IV, and V without key signature, 
	#then adds key sig 
	possibleChords = []
	tonic = 1
	second = 2
	fourth = 4
	fifth = 5
	numNotesInScale = 7 
	interval = 2
	chordTypes = [tonic, second, fourth, fifth] #different types of chords 
	try: 
		for chordType in chordTypes: 
			tonicKeyIndex = data.scale.index(data.keySig[0])
			startingKey = data.scale[(tonicKeyIndex+chordType-1)%numNotesInScale] 
			#data.keySig is in format 'A major'
			startingKeyIndex = data.scale.index(startingKey)
			possibleChords += [(startingKey+
			data.scale[(startingKeyIndex+interval)%numNotesInScale]+
	        	data.scale[(startingKeyIndex+2*interval)%numNotesInScale])]
		return possibleChordsInKeySig(data, possibleChords)
	except: 
		messagebox.showinfo("Cadenza", 
		"Make sure you enter a valid key!")

def divideByThree(anyList): 
    three = 3
    newList = []
    for val in anyList: 
        newList += [val//three]
    return newList

def playChord(data, chordList, count):
    indicesOfThree = divideByThree(data.missingChords)
    if (count in indicesOfThree and data.solved == False): 
        silence = AudioSegment.from_wav(
            "Media/Piano/silence4.wav")
        play(silence)
    else: 
        noteWithBeat = int(data.timeSig[2])
        if (noteWithBeat == 4): 
            time = data.quarterNote
        elif (noteWithBeat == 2): 
            time = data.halfNote
        elif (noteWithBeat == 8): 
            time = data.eighthNote
        note1 = AudioSegment.from_wav(
            "Media/Piano/"+chordList[0]+"4.wav"
            )[:time]
        note2 = AudioSegment.from_wav(
            "Media/Piano/"+chordList[1]+"4.wav"
            )[:time]
        note3 = AudioSegment.from_wav(
            "Media/Piano/"+chordList[2]+"4.wav"
            )[:time]
        chordtriad = note1.overlay(note2)
        chordactual = chordtriad.overlay(note3)
        play(chordactual)

def changeChordStringToList(chord): 
    chordList = []
    for i in range(len(chord)): #letter or accidental 
        if (chord[i] == '#' or chord[i] == 'b'):
            chordList.pop()
            accidental = chord[i]
            accNote = chord[i-1] 
            #the note right before is the note with the accidental
            chordList += [accNote+accidental] 
            #if chord = 'C#EG#', chordList = ['C#', 'E', 'G#']
        else:
            chordList += [chord[i]]
    return chordList 

def chordListWithOctaves(chord): 
    chordNoOctaves = changeChordStringToList(chord)
    chordListWithOctaves = []
    for note in chordNoOctaves:
        chordListWithOctaves += [note+'4'] 
        #so every note is played in octave 4 
    return chordListWithOctaves 
    #chordListWithOctaves returns ['C#4', 'E4', 'G4']

def convertSongOfChordTypesToNotes(data): 
    chordNotes = [] #chordNotesSong is a 2d list 
    chordNotesSong = []
    listOfChords = possibleChords(data) 
    #possibleChords returns ['C#EG', 'DFA', 'FAC', 'GBD']
    for chordType in data.song: #data.song is in form [1, 2, 4, 5]
        if (chordType == 1):
            chordNotes += [listOfChords[0]]
        elif (chordType == 2): 
            chordNotes += [listOfChords[1]]
        elif (chordType == 4): 
            chordNotes += [listOfChords[2]]
        elif (chordType == 5): 
            chordNotes += [listOfChords[3]] 
            #chordNotes is in form ['CEG', 'FAC'...]
    data.chords = chordNotes 
    return chordNotes

def playSong(data): 
    if (data.jazzMode): 
        makeJazzBeat(data)
    else: 
        count = -1
        for chord in convertSongOfChordTypesToNotes(data): 
        #['CEG', 'FAC', ...]
            count += 1 #counts the chords 
            playChord(data, changeChordStringToList(chord), count) #[C, E, G]


# Research on Markov Chains done by talking with
# Anja Kalaba and Sara Adkins from RobOrchestra

def generateNewSong(data, currChord=None, song=None):
    numNotesPerMeasure = int(data.beatsPerMeasure)
    numMeasures = 5
    first = 1
    second = 2
    fourth = 4
    fifth = 5 # these are types of cadences 
    thirtyPerc = 30
    sixtyPerc = 60
    oneHPercent = 100
    seventyPerc = 70
    fiftyPerc = 50
    sixtyPerc = 60
    eightyPerc = 80
    if (song == None): 
        song = []
    if (len(song) == numNotesPerMeasure*numMeasures): 
        return song #use backtracking to make sure it ends on a 1 chord! 
    if (currChord == None): 
        currChord = random.choice([first, second, fourth, fifth])
    randomNum = random.randint(0, oneHPercent)
    if (currChord == fourth): 
        if (0 < randomNum < sixtyPerc): #60% chance it goes to chord I 
            song += [first]
        elif (sixtyPerc < randomNum < oneHPercent): #40% chance it goes to chord V
            song += [fifth]
    if (currChord == fifth):
        if (0 < randomNum < fiftyPerc): 
            song += [first]
        elif (fiftyPerc < randomNum < eightyPerc): 
            song += [fourth]
        elif (eightyPerc < randomNum < oneHPercent): 
            song += [second]
    if (currChord == first): 
        if (0 < randomNum < seventyPerc): 
            song += [fourth]
        elif (seventyPerc < randomNum < oneHPercent): 
            song += [fifth]
    if (currChord == second): 
        if (0 < randomNum < thirtyPerc): 
            song += [fifth]
        elif (thirtyPerc < randomNum < oneHPercent): 
            song += [first]
    return generateNewSong(data, song[-1], song) 

def isLegalCadence(data, currNoteIndex, cadences):
    if (cadences[-1] != 'I' or cadences[-1] != 'V'): 
        return False 
    if (cadences[-1] == cadences[-2]): 
        return False
    if (cadences[-1] == 'I'): 
        if (cadences[-2] != 'V' or cadences[-2] != 'IV'): 
            return False


def drawStaff(canvas, data): 
    xMargin = 50 #from edges of canvas 
    yMargin = 90
    lineHeight = 15 #distance between each line of the staff
    lineMargin = 40 #distance between bottom line of one staff and top of next
    measuresPerLine = 5
    totalStaffHeight = lineHeight*(measuresPerLine-1)
    staffWidth = data.width-2*xMargin 
    measureWidth = staffWidth//measuresPerLine
    numberOfStaffs = data.height//(totalStaffHeight+lineMargin)
    for measure in range(1, measuresPerLine+1): 
        canvas.create_line(xMargin, 
            yMargin+measure*lineHeight, 
            data.width-xMargin,     
            yMargin+measure*lineHeight)
    margin = 32
    canvas.create_text(data.width//2, margin, text = "Create Your Cadence!", 
        font = "Helvetica 30 bold")
    for measure in range(0, measuresPerLine+1): 
        canvas.create_line(xMargin+measureWidth*(measure), 
        yMargin+lineHeight, 
        xMargin+measureWidth*(measure), 
        yMargin+lineHeight+
            totalStaffHeight)
            

def detectTrebleNote(data): 
    #make a list of all the top lines of each staff 
    yMargin = 90
    xMargin = 50
    measuresPerLine = 5 
    lineHeight = 15
    lineMargin = 40 #distance between bottom line of one staff and top of next
    totalStaffHeight = lineHeight*(measuresPerLine-1)
    numberOfStaffs = data.height//(totalStaffHeight+lineMargin)
    topLine = yMargin 
    mouseToEyeError = 10 # since when you click on a spot, 
    #its y position is 10 pixels off from where you think you clicked 
    r = 0.3 
    G5, F5, E5, D5, C5 = -0.5, 0, 0.5, 1, 1.5
    B4, A4, G4, F4, E4, D4, C4 = 2, 2.5, 3, 3.5, 4, 4.5, 5
    distanceFromTopLine = (data.notesY[-1]-topLine-mouseToEyeError)/lineHeight
    if (G5-r < distanceFromTopLine < G5+r): 
        data.trebleNotes += ['G']
    if (F5-r < distanceFromTopLine < F5+r): 
        data.trebleNotes += ['F']
    elif (E5-r < distanceFromTopLine < E5+r): 
        data.trebleNotes += ['E']
    elif (D5-r < distanceFromTopLine < D5+r): 
        data.trebleNotes += ['D']
    elif (C5-r < distanceFromTopLine < C5+r): 
        data.trebleNotes += ['C']
    elif (B4-r < distanceFromTopLine < B4+r): 
        data.trebleNotes += ['B']
    elif (A4-r < distanceFromTopLine < A4+r): 
        data.trebleNotes += ['A']
    elif (G4-r < distanceFromTopLine < G4+r): 
        data.trebleNotes += ['G']
    elif (F4-r < distanceFromTopLine < F4+r): 
        data.trebleNotes += ['F']
    elif (E4-r < distanceFromTopLine < E4+r): 
        data.trebleNotes += ['E']
    elif (D4-r < distanceFromTopLine < D4+r): 
        data.trebleNotes += ['D']
    elif (C4-r < distanceFromTopLine < C4+r): 
        data.trebleNotes += ['C']

def undo(data): #unplaces a note 
    data.notesPositions.pop()
    data.notesY.pop()
    data.notesX.pop()
    data.trebleNotes.pop()

def inversion(data, currChord, missingChords): 
#checks if the currchord is an inversion of any of the missingChords
    root = (currChord[0]) 
    third = (currChord[1])
    fifth = (currChord[2])
    regular = [root]+[third]+[fifth]
    firstInv = [third]+[fifth]+[root]
    secondInv = [fifth]+[root]+[third]
    if regular in missingChords:
        return regular
    elif (firstInv in missingChords): 
        data.inversion = 'first inversion'
        return firstInv
    elif (secondInv in missingChords): 
        data.inversion = 'second inversion'
        return secondInv 
    else: 
    #if is currChord in treble chords not inversion of any of missing chords  
        return False 

def makeIntoGroupsOfThreeWithAcc(anyList): 
    groupOfThree = 3
    if (len(anyList) % groupOfThree != 0): return None 
    count = -1
    chord = []
    numNotesInChord = 3
    chordList = []
    for note in anyList:
        if (isinstance(note, Note)): 
            note = str(note)[:2] #makes C#4 into 'C#'!!
        count += 1
        chord += [note]
        if (count == numNotesInChord-1): 
            chordList += [chord]
            count = -1
            chord = []
    return chordList 

def makeIntoGroupsOfThree(data, anyList): 
    groupOfThree = 3
    if (len(anyList) % groupOfThree != 0): return None 
    count = -1
    chord = []
    numNotesInChord = 3
    chordList = []
    for note in anyList:
        if (isinstance(note, Note)): 
            note = str(note)[0] #makes C4 into 'C'!!
        count += 1
        chord += [note]
        if (count == numNotesInChord-1): 
            chordList += [chord]
            count = -1
            chord = []
    return chordList 

def checkCorrect(data):
    correctInversion = False 
    score = 10 
    numNotes = 3
    if (len(data.trebleNotes)%numNotes != 0):
        messagebox.showinfo("Cadenza", "Make sure the"
            " number of notes you have is a multiple of three!")
        return None
    trebleListInChords = makeIntoGroupsOfThree(data, data.trebleNotes) 
    missingChords = makeIntoGroupsOfThree(data, data.notesOfMissingChords)
    #missingChords is a list of objects 
    if (data.difficultyLevel == 2): #hard - must get the chords exactly 
        for chord in trebleListInChords: 
            if chord in missingChords: 
                missingChords.remove(chord) 
            if (missingChords == []): #then you did it correctly! 
                data.score += score
                data.solved = True
                messagebox.showinfo("Cadenza", "Awesome job!"
                    " Your score has been updated. "
                    "Click 'Make Song' to generate"
                    " a new song, or click 'Done' to exit the game.") 
            elif (missingChords != []):
                messagebox.showinfo("Cadenza", "Not quite!"
                    " You can edit your chord and try again.") 
    if (data.difficultyLevel == 1): #easy - allows for inversions 
        for chord in trebleListInChords: 
            if chord in missingChords: # is it exactly there? 
                missingChords.remove(chord) 
            elif (chord not in missingChords): 
            # if not, check if it is an inversion 
                correctInversion = inversion(data, chord, missingChords)
                if (correctInversion != False): #if doesn't return False 
                    missingChords.remove(correctInversion)
        if (missingChords == [] and correctInversion == False): 
            data.score += score #then you did it but w/o inversions  
            data.solved = True
            messagebox.showinfo("Cadenza", "Awesome job!"
                " Your score has been updated. Click 'Make Song' to generate"
                " a new song, or click 'Done' to exit the game.")
        elif (missingChords == [] and correctInversion != False): 
            messagebox.showinfo("Cadenza", "Great "+data.inversion+"!"
                    " Your score has been updated.")
            data.score += 2*score #bonus points if did an inversion 
            data.solved = True
        elif (missingChords != []): 
            messagebox.showinfo("Cadenza", "Not quite!"
                " You can keep going or edit your chord and try again.") 
                

###############################
# success mode
###############################
def successKeyPressed(event, data): 
    if (event.keysym == 'r'): 
        init(data) 

def successRedrawAll(canvas, data): 
    drawImage(canvas, "Media/ending.jpg", 
            data.width, data.height, data.width//2, data.height//2)
    margin = 120 
    if (data.notes != []): 
        numNotes = 3
        randomNotes = random.sample(data.notes, numNotes) 
        for note in data.notes: 
            if not (note in randomNotes): 
                note.draw(data, canvas) 
    blockm = 10
    sIncrement = 5
    canvas.create_rectangle(0, data.height//2-blockm, data.width//sIncrement, 
        data.height//2+blockm, fill = "white", outline = "white")
    canvas.create_rectangle(data.width-data.width//sIncrement+blockm, 
        data.height//2-blockm, 
        data.width, data.height//2+blockm, fill = "white", outline = "white")
    canvas.create_text(data.width//2, data.height//2, text = "Well Done", 
        font = "Helvetica 100 bold", fill = "white")
    canvas.create_text(data.width//2, data.height//2+margin, 
        text = "Press R To Play Again", font = "Helvetica 50 bold", 
        fill = "white")

################################
class Note(object): 
    def __init__(self, note, chordNumber, measureNumber): 
        self.note = note #in form of 'F5'
        self.measureNumber = measureNumber
        self.chordNumber = chordNumber 
        #which chord in measure you are - eg. 1, 2, 3rd chord
        r = 0.3 
        dictionaryOfKeysAndLocations = {'G5':-0.5, 'G#5': -0.5, 'Gb5': -0.5, 
            'F5': 0, 'F#5': 0, 'Fb5': 0, 'E5': 0.5, 'E#5': 0.5, 'Eb5': 0.5, 
            'D5': 1, 'D#5': 1, 'Db5': 1, 'C5': 1.5, 'C#5': 1.5, 'Cb5': 1.5,
            'B4': 2, 'B#4': 2, 'Bb4': 2, 'A4': 2.5, 'A#4': 2.5, 'Ab4': 2.5,
            'G4': 3, 'G#4': 3, 'Gb4': 3, 'F4': 3.5, 'F#4': 3.5, 'Fb4': 3.5,
            'E4': 4, 'E#4': 4, 'Eb4': 4, 'D4': 4.5, 'D#4': 4.5, 'Db4': 4.5, 
            'C4': 5, 'C#4': 5, 'Cb4': 5}
        intervalFromTop = dictionaryOfKeysAndLocations[self.note]
        lineHeight = 15
        distFromTop = intervalFromTop*lineHeight
        self.distFromTop = distFromTop
    
    def draw(self, data, canvas): 
        yMargin = 90
        xMargin = 58
        margin = 20
        measuresPerLine = 5
        staffWidth = data.width-2*xMargin 
        measureWidth = staffWidth//measuresPerLine
        spacePerChord = (measureWidth)//int(data.beatsPerMeasure)
        width = 15
        height = 40
        eighthNote = 8 
        halfNote = 2
        quarterNote = 4
        totalStaffHeight = 75
        if (data.timeSig != None): 
            noteWithBeat = int(data.timeSig[2]) #data.timeSig in form of 3/8 
        if (self.note[0] == "C"): 
            width = 30
            height = 60
            if (noteWithBeat == quarterNote):
                marginY = 3
                drawImage(canvas, "Media/quarternoteCModified.gif", 
                width, height, (xMargin+measureWidth*self.measureNumber+margin+
                spacePerChord*self.chordNumber), 
                yMargin+self.distFromTop-marginY)
            elif (noteWithBeat == eighthNote): 
                marginX = 3
                marginY = 2
                width = 18
                drawImage(canvas, "Media/eighthNoteC.gif", 
                width, height, (xMargin+measureWidth*self.measureNumber+margin+
                spacePerChord*self.chordNumber-marginX), 
                yMargin+self.distFromTop-marginY)
            elif (noteWithBeat == halfNote): 
                width = 15
                height = 37
                drawImage(canvas, "Media/halfNoteC.gif", 
                width, height, (xMargin+measureWidth*self.measureNumber+margin+
                spacePerChord*self.chordNumber), 
                yMargin+self.distFromTop)
        else: #note is not a C
            if (noteWithBeat == quarterNote):
                drawImage(canvas, "Media/quarternote3Modified.gif", 
                    width, height, (xMargin+measureWidth*self.measureNumber+
                    margin+spacePerChord*self.chordNumber), 
                    yMargin+self.distFromTop)
            elif (noteWithBeat == eighthNote): 
                drawImage(canvas, "Media/eighthnoteModified.gif", 
                width, height, (xMargin+measureWidth*self.measureNumber+margin+
                spacePerChord*self.chordNumber), 
                yMargin+self.distFromTop)
            elif (noteWithBeat == halfNote): 
                drawImage(canvas, "Media/halfnoteModified.gif", 
                width, height, (xMargin+measureWidth*self.measureNumber+margin+
                spacePerChord*self.chordNumber), 
                yMargin+self.distFromTop)
    
    def __repr__(self): 
        return self.note

def transcribeSongToStaff(data): #[C, E, G]
    chordNotesInTwoDArray = []
    for chord in convertSongOfChordTypesToNotes(data): 
        chordNotesInTwoDArray += [chordListWithOctaves(chord)] 
        #in form of [[C, E, G], [A, B, C]]
    song = chordNotesInTwoDArray
    chordNumber = -1
    measureNumber = 0
    notesInMeasure = int(data.beatsPerMeasure)
    notes = [] 
    for chord in song:
        chordNumber += 1
        for letter in chord: 
            data.notes.append(Note(letter, chordNumber, measureNumber))
        if (chordNumber == notesInMeasure-1): 
            measureNumber += 1
            chordNumber = -1
    chordsToRemove(data)

def drawNote(canvas, data): #x and y correspond to event.x and event.y
    r = 5
    stem = 15
    addedStem = 5
    width = 30
    height = 48
    margin = 10 
    if (data.timeSig != None): 
        noteWithBeat = int(data.timeSig[2])
    quarterNote = 4
    eighthNote = 8 
    halfNote = 2
    for (x,y,isDrawingC) in data.notesPositions:
        if (isDrawingC):
            if (noteWithBeat == quarterNote):
                drawImage(canvas, "Media/quarternoteCblue.gif", 
                width, height, x, y-margin)
            elif (noteWithBeat == eighthNote): 
                width = 18 
                drawImage(canvas, "Media/eighthNoteCblue.gif", 
                width, height, x, y-margin)
            elif (noteWithBeat == halfNote): 
                width = 20
                drawImage(canvas, "Media/halfNoteCblue.gif", 
                width, height, x, y-margin)
        else: 
            if (noteWithBeat == quarterNote): 
                canvas.create_oval(x, y, x+2*r, y+2*r, 
                    fill = "sky blue", outline = "sky blue") 
                canvas.create_line(x+2*r, y-stem, x+2*r, 
                    y+addedStem, fill = "sky blue")
            elif (noteWithBeat == eighthNote):
                width = 15
                height = 45
                margin = 15
                drawImage(canvas, "Media/eighthnoteblue.gif", 
                width, height, x, y-margin)
            elif (noteWithBeat == halfNote):
                width = 15
                drawImage(canvas, "Media/halfnoteblue.gif", 
                width, height, x, y-margin)


def chordsToRemove(data): 
    numNotes = 3
    possibleThirdIndices = len(data.notes)//numNotes
    possibleThirdNotes = list(range(0, possibleThirdIndices-1))
    numChordsToRemove = data.numMissingChords
    randomChords = random.sample(possibleThirdNotes, numChordsToRemove)
    #randomChords will return [1, 2, 3]
    multiplesOfThree = []
    notesInChord = 3
    for beginningMissingChordIndex in randomChords: 
        multiplesOfThree += [beginningMissingChordIndex*notesInChord]
    data.missingChords = multiplesOfThree
        # a list of the beginning indices for the notes in the chords to remove 
    return data.missingChords #missingChords = [0, 3, 6]

def createListOfNotesOfMissingChords(data): 
    numNotes = 3
    notesWithMissingChords = copy.copy(data.notes)
    if (data.notes != []): 
        for chord in data.missingChords: #[1, 2, 3]
            for i in range(numNotes): 
                data.notesOfMissingChords += [notesWithMissingChords.pop(chord)]
    data.notesWithMissingChords = notesWithMissingChords

def extendToThree(anyList): 
    numNotes = 3
    newList = []
    for val in anyList: 
        for i in range(numNotes):
            newList += [val+i]
    return newList

def cadenceRedrawAll(canvas, data):
    drawImage(canvas, "Media/cadencebg.jpg", 
            data.width, data.height, data.width//2, 
            data.height//2)
    xTime = 70
    y = 50
    alty = 58
    width = 155 
    height = 40 
    xKey = 230
    xSong = 390
    xPlay = 550
    xCheck = 50
    yCheck = data.height//2-50
    xScore = 50
    yScore = data.height//2
    xAnswer = 50
    yAnswer = data.height//2+50
    xNote = data.width-150
    yNote = data.height//2-10
    xDiff = xNote-width//2
    yDiff = yNote+35
    pressedColor = 'light sea green'
    Button(width, height, xTime, y, "Enter Time Signature").draw(canvas, data)
    Button(width, height, xKey, y, "Enter Key Signature").draw(canvas, data)
    Button(width, height, xSong, y, "Make Song").draw(canvas, data)
    Button(width, height, xPlay, y, "Play Song").draw(canvas, data)
    Button(width, height, xTime, data.height-alty, "Undo").draw(canvas, data)
    Button(width, height, xKey, data.height-alty, "Done").draw(canvas, data)
    if (data.drawingC): 
        Button(width, height, xSong, data.height-alty, "Draw C Note",
            boxColor=pressedColor).draw(canvas, data)
    elif (not data.drawingC):  
        Button(width, height, xSong, data.height-alty, "Draw C Note").draw(canvas, data)
    if (data.jazzMode): 
        Button(width, height, xPlay, data.height-alty, "Jazzify",
            boxColor=pressedColor).draw(canvas, data)
    elif (not data.jazzMode): 
        Button(width, height, xPlay, data.height-alty, "Jazzify").draw(canvas, data)
    Button(width, height, xCheck, yCheck, "Check").draw(canvas, data)
    Button(width, height, xScore, yScore, "Score: "+str(data.score)).draw(canvas, data)
    Button(width, height, xDiff, yDiff, "Challenge").draw(canvas, data)
    Button(width, height, xAnswer, yAnswer, "Get Answer").draw(canvas, data)
    if (data.isCreatingNotes):
        canvas.create_text(xNote, yNote, text = "Create Mode: ON", 
            font = "Helvetica 20 bold", fill = "light sea green") 
    elif (not data.isCreatingNotes): 
        canvas.create_text(xNote, yNote, text = "Create Mode: OFF",
            font = "Helvetica 20 bold") 
    toggleM = 18
    canvas.create_text(xNote, yNote+toggleM, text =  "(Press N to Toggle)",
        font = "Helvetica 15 bold")
    # for printing the missing notes 
    if (data.printingSong and data.notes != []):
        missingChordList = extendToThree(data.missingChords)
        note = 0 
        ctr = 0 
        while (note < len(data.notes)): 
            while (ctr < len(missingChordList)): 
                if (missingChordList[ctr] == note):
                    note += 2
                    break
                ctr += 1
            if ctr == len(missingChordList): 
                (data.notes[note]).draw(data, canvas)
            ctr = 0
            note += 1
    drawStaff(canvas, data) 
    xMargin = 48 #from edges of canvas 
    yMargin = 90
    mX = 15
    mY = 50
    widthImage = 40
    heightImage = 70
    drawImage(canvas, "Media/trebleclefModified.gif", 
        widthImage, heightImage, xMargin+mX, yMargin+mY)
    textX = data.width//2
    textY = 100
    textYCadences = 125
    textYMainMenu = 75
    canvas.create_text(data.width//2, data.height-textY, text = "Press H"
        " for Help Screen", font = "Helvetica 20 bold")
    canvas.create_text(data.width//2, data.height-textYCadences, text = "Press" 
        " C for Cadence Reference", 
        font = "Helvetica 20 bold")
    canvas.create_text(data.width//2, data.height-textYMainMenu, 
        text = "Press M for Main Menu", 
        font = "Helvetica 20 bold")
    drawNote(canvas, data)


def drawImage(canvas, path, width, height, x, y):
    image = PIL.Image.open(path)
    imageWidth, imageHeight = image.size
    newImageWidth, newImageHeight = imageWidth//2, imageHeight//2
    image = image.resize((width, height), PIL.Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    label = Label(image=photo)
    label.image = photo
    canvas.create_image(x, y, image = photo)


def run(width=300, height=300): #run function taken from 112 class notes 
#https://www.cs.cmu.edu/~112/notes/notes-animations-examples.html
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 
    init(data)
    root = Tk()
    root.wm_title("CADENZA")
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()  
    print("bye!")

run(800, 700)