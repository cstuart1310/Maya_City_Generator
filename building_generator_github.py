#Maya City Generator - Callum Stuart, Birmingham City University Visual Effects
from fnmatch import translate
from typing import NewType
import maya.cmds as cmds
import random
import time
import maya.mel as mel


versionNo=6

layoutMode="Uniform"
effects=[]#Effects to apply to a building
pastPositions=[]

midFacesX=[53,51,63,61,71,73,23,21,11,13,3,1]




#functions----------------------------------------

#Gets a random value between ranges (Shorter than using full length command each time which makes better readability)
def randFloat(min,max):
    return random.uniform(min,max)
def randInteger(min,max):
    return random.randint(min,max)

#Applies effects from the list to the currently selected building
def addBuildingEffects(effect,buildingName):
    print("Applying",effect,"to",buildingName)

    if effect=="addWindows":#Adds windows
        cmds.polyExtrudeFacet(buildingName+'.f[50:74]',buildingName+'.f[0:24]',buildingName+'.f[100:128]',buildingName+'.f[129:149]',kft=False, ltz=-.75, ls=(.5, .8, 0),smoothingAngle=45)

    elif effect=="scaleTop":#Scale top in
        cmds.select(buildingName+'.e[30:34]')
        cmds.select(buildingName+'.e[25:29]',add=True)
        cmds.scale(randFloat(1,1.5),randFloat(1,1.5),1)

    elif effect=="bevel":#Bevels edges
        edgeRingVal=randInteger(0,130)
        print("Edge ring being beveled:",edgeRingVal)
        cmds.polySelect(buildingName, edgeRing=edgeRingVal)
        cmds.polyBevel(segments=randInteger(1,12),offset=randFloat(0.1,0.9),offsetAsFraction=True) #Applies bevel (offset=fraction value in maya ui)

    elif effect=="rotate":
        rotateVal=(0,randFloat(5,359),0)
        cmds.xform(buildingName,rotation=rotateVal,worldSpace=True,centerPivots=True,absolute=True)#Rotates the building


#main-------------------------------------------------

class ProgressClass(object):#Class used for the progress bar
    def updateProgress(self):#Function used to update the progress bar and close it when finished
        cmds.progressBar(self.progressBar, edit=True, step=1,isInterruptable=True)
        self.progressVal+=1#Increments progress val by 1 (Less intense then querying the progress bar all the time)
        if self.progressVal==self.maxProgress:
            # progressText=str(self.progressVal,"/",self.maxProgress)
            # cmds.text(self.finishedText,edit=True,label=progressText)
            cmds.deleteUI(self.window, window=True)#Closes window


    def startProgress(self,maxProgress):#Opens the progress bar
        self.maxProgress=maxProgress
        self.progressVal=0
        self.window = "City Generation Progress"

        if cmds.window(self.window, exists = True):#Checks if existing window is open
            cmds.deleteUI(self.window, window=True)#Closes existing window

        #Window
        self.title = ("City Generation Progress")
        self.size = (800, 800)
        self.window = cmds.window(self.window, title=self.title,widthHeight=self.size)#Creates the window
        
        cmds.columnLayout(adjustableColumn = True)#create layout
        
        cmds.text(self.title)# title text
        
        cmds.separator(height=20)# separator

        self.progressBar = cmds.progressBar(maxValue=maxProgress, width=300,visible=True,backgroundColor=[0,0,0])#Creates the progress bar in the UI window
        self.finishedText=cmds.text("Finished!",visible=False)
        cmds.showWindow()#Displays the window




#Menu Setup
class BG_Window(object):
    def __init__(self):
        #Window
        self.window = "BG_Window"
        self.title = ("Building Generator v"+str(versionNo))
        self.size = (600, 400)

        if cmds.window(self.window, exists = True):#Checks if existing window is open
            cmds.deleteUI(self.window, window=True)#Closes existing window
        
        self.window = cmds.window(self.window, title=self.title,widthHeight=self.size)#Creates the window
        
        #create layout
        cmds.columnLayout(adjustableColumn = True)
        # title text
        cmds.text(self.title)
        # separator
        cmds.separator(height=20)

        self.inpLayoutMode = cmds.optionMenu( label='Layout mode',width=200)#Creates the dropdown menu for the layout mode options
        cmds.menuItem(label='Uniform')#Layout mode option 1
        cmds.menuItem(label='Uniform with spacing variation')
        cmds.menuItem(label='Random')#Layout mode option
        

        #Var inputs
        self.inpBuildingRange = cmds.floatFieldGrp( numberOfFields=2, label='Building distance range:', value1=-1000, value2=1000)
        self.inpBuildingHeight = cmds.floatFieldGrp( numberOfFields=2, label='Building Height range:', value1=10, value2=100)
        self.inpBuildingWidth = cmds.floatFieldGrp( numberOfFields=2, label='Building Width range:', value1=10, value2=20)
        self.inpBuildingDepth = cmds.floatFieldGrp( numberOfFields=2, label='Building Depth range:', value1=10, value2=20)
        self.inpNoBuildings = cmds.intSliderGrp(field=True, label='Number of buildings:', minValue=1,maxValue=10000, value=1000)

        #Effect Tickboxes and sliders
        cmds.rowColumnLayout(nc=2)#Changes the layout so can have 2 items next to each other
        self.inpEffectAddWindows=cmds.checkBox(label='Add Windows',changeCommand=lambda x: self.toggleSliderLock(self.inpEffectAddWindowsChance))#Checkbox for toggling the effect. Lambda is used to define the changecommand without actually running it, so a variable can be passed and the one function can manage all slider toggles
        self.inpEffectAddWindowsChance = cmds.intSliderGrp(field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do

        self.inpEffectBevel=cmds.checkBox(label='Bevel Top edges',changeCommand=lambda x: self.toggleSliderLock(self.inpEffectBevelChance))
        self.inpEffectBevelChance = cmds.intSliderGrp(field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectScaleTop=cmds.checkBox(label='Scale Top Edges', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectScaleTopChance))
        self.inpEffectScaleTopChance = cmds.intSliderGrp(field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectRotate=cmds.checkBox(label='Rotate building', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectRotateChance))
        self.inpEffectRotateChance = cmds.intSliderGrp(field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)


        cmds.separator(style='none')#Resets the layout to one after the other
        cmds.columnLayout(adjustableColumn = True)

        #Gen button
        self.buildBtn = cmds.button( label='Create Buildings', command=self.genBuildings,width=500)
        self.buildBtn = cmds.button( label='Undo Last City', command=self.removeBuildings,width=500)

        cmds.showWindow()

    def toggleSliderLock(self,slider,*args):#Toggles a slider bar (Needs to be a function as it's called before the UI elements being toggled are made)
        print(slider)
        try:#Used so doesn't crash when running before the sliders exist            
            if  cmds.intSliderGrp(slider,query=True,enable=True):
                cmds.intSliderGrp(slider,edit=True,enable=False)
            else:
                cmds.intSliderGrp(slider,edit=True,enable=True)
        except AttributeError as e:
            print(e)
        return None

    def removeBuildings(self, *args):#Removes the last generated city
        try:
            cmds.delete("Buildings") #Deletes the buildings group
            cmds.delete("Ground_Plane") #Deletes the ground plane
        except ValueError:#Catches in case the user has deleted one or more of these elements
            pass#Does nothing but an except needs to do "something" so this is here

    def useEffect(self,effectChance):#Returns true or false on whether or not to apply an effect based on its' inputted likelyhood
        useVal=randInteger(1,100)#Produces a random value between 1 and 100
        if useVal<=effectChance:#If the random val is within the range of 0-effectChance
            return True
        else:
            return False


    def genBuildings(self, *args):
        
        #Gets data from inp boxes (Only used in this function so no need for self)
        layoutMode=cmds.optionMenu(self.inpLayoutMode,query=True,value=True) #Gets the layout mode by querying the optionmenu
        valBuildingRangeMin= cmds.floatFieldGrp(self.inpBuildingRange, query=True, value1=True)#Gets the value by querying the input box
        valBuildingRangeMax = cmds.floatFieldGrp(self.inpBuildingRange, query=True, value2=True)#Gets the value by querying the input box
        valBuildingHeightMin = cmds.floatFieldGrp(self.inpBuildingHeight, query=True, value1=True)#Gets the value by querying the input box
        valBuildingHeightMax = cmds.floatFieldGrp(self.inpBuildingHeight, query=True, value2=True)#Gets the value by querying the input box
        valBuildingWidthMin = cmds.floatFieldGrp(self.inpBuildingWidth, query=True, value1=True)#Gets the value by querying the input box
        valBuildingWidthMax = cmds.floatFieldGrp(self.inpBuildingWidth, query=True, value2=True)#Gets the value by querying the input box
        valBuildingDepthMin = cmds.floatFieldGrp(self.inpBuildingDepth, query=True, value1=True)#Gets the value by querying the input box
        valBuildingDepthMax = cmds.floatFieldGrp(self.inpBuildingDepth, query=True, value2=True)#Gets the value by querying the slider bar (Or input box)
        valNoBuildings = cmds.intSliderGrp(self.inpNoBuildings, query=True, value=True)

        #misc variables that need to be set once outside the loop so they can iterate during the loop
        prevPosition=valBuildingRangeMin#Used for placing the first building in uniform mode (So it's placed in the first corner)
        zVal=valBuildingRangeMin#Used to lay out the buildings in rows

        effects=[]#Clears effects on each re-run
        
        #gets effects (In the order that works best to apply in)
        if cmds.checkBox(self.inpEffectScaleTop, query=True, value=True):#Queries if check box is checked
            effects.append(["scaleTop",cmds.intSliderGrp(self.inpEffectScaleTopChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectAddWindows, query=True, value=True):#Queries if check box is checked
            effects.append(["addWindows",cmds.intSliderGrp(self.inpEffectAddWindowsChance, query=True, value=True)])#Adds the effect and its % chance of being applied to an array
        if cmds.checkBox(self.inpEffectBevel, query=True, value=True):#Queries if check box is checked
            effects.append(["bevel",cmds.intSliderGrp(self.inpEffectBevelChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectRotate, query=True, value=True):#Queries if check box is checked
            effects.append(["rotate",cmds.intSliderGrp(self.inpEffectRotateChance, query=True, value=True)])#Adds the effect to the list of effects to use

        #main loop
        if cmds.objExists('Buildings'):
            cmds.confirmDialog(title="Warning!",message="A group named Buildings already exists, generated buildings will be placed into it")
        else:
            cmds.group(empty=True, name='Buildings')#Creates the group that the buildings will be placed into
        #cmds.polyPlane(width=valBuildingRangeMax*2,height=valBuildingRangeMax*2,name="Ground Plane") #creates ground plane
        
        print("Layout Mode:",layoutMode)

        ProgressClass.startProgress(self,valNoBuildings)#Opens up the progress bar window, passing the maximum number of buildings to it so it always steps by 1 (Cant step by a float val)

        for buildingNo in range(1,valNoBuildings+1):#Plus 1 so first building is building 1 but still exact range
            buildingName=("Building_"+str(buildingNo))#Names the buildings in the format Building_1

            #generates dimensions for the building
            buildingHeight=randFloat(valBuildingHeightMin,valBuildingHeightMax)
            buildingWidth=randFloat(valBuildingWidthMin,valBuildingWidthMax)
            buildingDepth=randFloat(valBuildingDepthMin,valBuildingDepthMax)

            cmds.polyCube(width=buildingWidth,height=buildingHeight,depth=buildingDepth,name=buildingName,subdivisionsX=5,subdivisionsY=5, subdivisionsZ=5)#Creates the cube to be morphed into a building
            
            #Generates the position for the building to be placed (Spawns at 0,0 by default)
            if layoutMode=="Random":#Randomly places buildings (May cause collisions)
                buildingPosition=[randFloat(valBuildingRangeMin,valBuildingRangeMax),buildingHeight/2,randFloat(valBuildingRangeMin,valBuildingRangeMax)] #Divs height by 2 because buildings are placed at 0 so half clips below
            
            elif layoutMode=="Uniform":#Places buildings in a grid format with set spacing
                buildingPosition=[prevPosition,buildingHeight/2,zVal]
                prevPosition=prevPosition+(buildingWidth*2)
                if prevPosition*2>valBuildingRangeMax:#If the building goes out of range
                    prevPosition=valBuildingRangeMin#Resets the building to the left side
                    zVal=zVal+buildingDepth*3 #Starts placing buildings on the next row
            
            elif layoutMode=="Uniform with spacing variation":#Places buildings in a grid format with random (within range) spacing
                buildingPosition=[prevPosition,buildingHeight/randFloat(1.5,2.5),zVal]
                prevPosition=prevPosition+(buildingWidth*randFloat(1.3,3.5))
                if prevPosition*2>valBuildingRangeMax:#If the building goes out of range
                    prevPosition=valBuildingRangeMin#Resets the building to the left side
                    zVal=zVal+buildingDepth*randFloat(2,3.5) #Starts placing buildings on the next row            

            cmds.xform(buildingName,translation=buildingPosition,worldSpace=True,centerPivots=True,absolute=True)#Moves the building to the generated position

           #Applies effects to current building

            for effectData in effects: #Loops through each piece of data in the 2d array
                effect=effectData[0]
                effectChance=effectData[1]
 
                print("Effect Data",effectData)
                if self.useEffect(effectChance)==True:#If it's selected to use the effect
                    addBuildingEffects(effect,buildingName)#Apply the effect
            cmds.parent(buildingName,"Buildings")
            
            ProgressClass.updateProgress(self)#Steps the progress bar by a value of 1 (The max val adjusts so stepping by 1 is fine)

print("\n"*30)
print("Starting...")
#Main startup
myWindow = BG_Window()



