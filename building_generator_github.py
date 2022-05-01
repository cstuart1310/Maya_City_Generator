#Maya City Generator - Callum Stuart, Birmingham City University Visual Effects
import maya.cmds as cmds
import random
import time
import maya.mel as mel

layoutMode="Uniform"
effects=[]#Effects to apply to a building
pastPositions=[]

#functions----------------------------------------

#Gets a random value between ranges (Shorter than using full length command each time which makes better readability)
def randFloat(min,max):
    return random.uniform(min,max)
def randInteger(min,max):
    return random.randint(min,max)

#Applies effects from the list to the currently selected building

def addBuildingEffects(self,effect,buildingName):
    print("Applying",effect,"to",buildingName)
    if effect=="addWindows":#Adds windows
        cmds.polyExtrudeFacet(buildingName+'.f[50:74]',buildingName+'.f[0:24]',buildingName+'.f[100:128]',buildingName+'.f[129:149]',kft=False, ltz=-.75, ls=(.5, .8, 0),smoothingAngle=45)
        self.windowBuildings.append(buildingName)#USed for the texture effect so it knows which buildings to add different glass mats to

    elif effect=="scaleTop":#Scale top in
        cmds.select(buildingName+'.e[30:34]')
        cmds.select(buildingName+'.e[25:29]',add=True)
        cmds.scale(randFloat(0.5,1.5),randFloat(0.5,1.5),1)
    
    elif effect=="addTower":#Scale top in
        cmds.select(buildingName+'.e[30:34]')
        cmds.select(buildingName+'.e[25:29]',add=True)
        cmds.scale(randFloat(0.5,1.5),randFloat(0.5,1.5),1)

    elif effect=="bevel":#Bevels edges
        edgeRingVal=randInteger(0,130)#Picks the edge (ring) to bevel        
        cmds.polyBevel(buildingName+".e[25:29]", offset=randFloat(0.1,0.9),offsetAsFraction=True )
        self.bevelBuildings.append(buildingName)#USed for the texture effect so it knows which buildings to add different glass mats to

        
    elif effect=="rotate":#Rotates the building along the Y axis only
        rotateVal=(0,randFloat(5,355),0)#Gets a random val (range is 5-355 so the rotation is always noticable)
        cmds.xform(buildingName,rotation=rotateVal,worldSpace=True,centerPivots=True,absolute=True)#Rotates the building

    elif effect=="applyMaterial":
        cmds.polyAutoProjection(buildingName+".f[*]", layoutMethod=0, insertBeforeDeformers=1, createNewMap=0, layout=0, sc=2, o=0, p=6, ps=0.2, ws=0,scale=(5,5,5) )#Performs an automatic UV on the building

        if len(self.materialsWindow.buildingMaterials)>0:#Checks to make sure there's something in the list else the random lib crashes
            randomMatBuilding=random.choice(self.materialsWindow.buildingMaterials)
            print("Assigning ",randomMatBuilding,"as the glass mat for",buildingName)
            cmds.sets(forceElement=randomMatBuilding)#Assigns a random material from the array to the selected object (A building)

        if buildingName in self.windowBuildings and len(self.materialsWindow.glassMaterials)>0:#If the selected buildings has had the addWindows effect applied. Checks to make sure there's something in the list else the random lib crashes
            randomMatGlass=random.choice(self.materialsWindow.glassMaterials)
            print("Assigning ",randomMatGlass,"as the glass mat for",buildingName)
            cmds.select(buildingName+'.f[50:74]',buildingName+'.f[0:24]',buildingName+'.f[100:128]',buildingName+'.f[129:149]')#Select the faces of the windows
            cmds.sets(forceElement=randomMatGlass)#Apply a random glass material
            cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)

        if len(self.materialsWindow.roofMaterials)>0:#Checks to make sure there's something in the list else the random lib crashes
            randomMatRoof=random.choice(self.materialsWindow.roofMaterials)
            print("Assigning ",randomMatRoof,"as the roof mat for",buildingName)
            
            if buildingName in self.bevelBuildings and buildingName in self.windowBuildings:
                cmds.select(buildingName+'.f[537:541]',buildingName+'.f[25:44]')#Select the faces of the roof (When beveled and windows added)
            if buildingName in self.bevelBuildings and buildingName not in self.windowBuildings:
                cmds.select(buildingName+'.f[150:154]',buildingName+'.f[20:39]')#Select the faces of the roof (When beveled)                
            else:
                cmds.select(buildingName+'.f[25:49]')#Select the faces of the roof (When flat)
                
            cmds.sets(forceElement=randomMatRoof)#Apply a random roof material
            cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)



#main-------------------------------------------------
class material_Window(object):#Class for the wiondows to do with the material selections

    def addMaterial(self,window,matList,TSList,*args):#Function used to add new materials to the given list
        print(self,window,matList,TSList)
        newMatList=matList+(cmds.textScrollList(self.sceneMaterialsTS, query=True, si=True))#Concats the original list and the user's selections into one list
        cmds.textScrollList(TSList,edit=True,append=newMatList)#Removes all items then appends the new array (Helps prevent duplicates)

        #Updates the global lists so the main class can access it
        
        if cmds.textScrollList(self.buildingMaterialsTSList, query=True, allItems=True) != None:#Checks if the list returns NONE becaise it's empty (This breaks everything and has annoyed me for about a day)
            self.buildingMaterials=cmds.textScrollList(self.buildingMaterialsTSList, query=True, allItems=True)
        
        if cmds.textScrollList(self.glassMaterialsTSList, query=True, allItems=True) != None:
            self.glassMaterials=cmds.textScrollList(self.glassMaterialsTSList, query=True, allItems=True)

        if cmds.textScrollList(self.roofMaterialsTSList, query=True, allItems=True) != None:
            self.roofMaterials=cmds.textScrollList(self.roofMaterialsTSList, query=True, allItems=True)
        
        
        print("Building Materials",self.buildingMaterials)
        print("Glass Materials",self.glassMaterials)
        print("Roof Materials",self.roofMaterials)


    def clearMaterialList(self,window,TSList,matList,*args):
        print("Clearing ",TSList)
        cmds.textScrollList(TSList,edit=True,removeAll=True)
        matList=matList.clear()

    def __init__(self,*args):
        self.buildingMaterials=[]
        self.glassMaterials=[]
        self.roofMaterials=[]

    def createMaterialUI(self,*args):
        self.buildingMaterials=[]
        self.glassMaterials=[]
        self.roofMaterials=[]


        self.window="Material List"
        self.title = "Material List"
        self.size = (1500, 800)

        self.materialListWindow=cmds.window(title='Materials List', width=200)

        cmds.columnLayout(rowSpacing=10, columnWidth=200)
        cmds.text("Scene Materials")
        sceneMaterialsList = cmds.ls(set=True)#Gets all materials (sets) in the scene
        self.sceneMaterialsTS=cmds.textScrollList(append=sceneMaterialsList,allowMultiSelection=True) #Shows all materials in the scene as a textScrollList
        
        cmds.rowColumnLayout(numberOfRows=4)#Changes to a 2 column layout for side-by-side buttons
        cmds.text( label='Building Materials' )#Title for this section
        self.buildingMaterialsTSList=cmds.textScrollList('Building Materials', append=self.buildingMaterials) 
        buildingMaterialsAppendButton=cmds.button( label='Add to Building Material list', command=lambda x: self.addMaterial(self,self.buildingMaterials,self.buildingMaterialsTSList))#Button to add selections to the list
        buildingMaterialsClearButton=cmds.button("Clear Building Material list",command=lambda x:self.clearMaterialList(self,self.buildingMaterialsTSList,self.buildingMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list
      

        cmds.text( label='Glass Materials' )#Title for this section
        self.glassMaterialsTSList=cmds.textScrollList('Glass Materials', append=self.glassMaterials) 
        glassMaterialsAppendButton=cmds.button( label='Add to Glass Materials list', command=lambda x: self.addMaterial(self,self.glassMaterials,self.glassMaterialsTSList))#Button to add selections to the list
        glassMaterialsClearButton=cmds.button("Clear Glass Materials list",command=lambda x:self.clearMaterialList(self,self.glassMaterialsTSList,self.glassMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list
 
        cmds.text( label='Roof Materials' )#Title for this section
        self.roofMaterialsTSList=cmds.textScrollList('Roof Materials', append=self.roofMaterials) 
        roofMaterialsAppendButton=cmds.button( label='Add to Roof Materials list', command=lambda x: self.addMaterial(self,self.roofMaterials,self.roofMaterialsTSList))#Button to add selections to the list
        roofMaterialsClearButton=cmds.button("Clear Roof Materials list",command=lambda x:self.clearMaterialList(self,self.roofMaterialsTSList,self.roofMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list
 
        
        cmds.separator()
        cmds.rowColumnLayout(numberOfRows=1)#Changes to a 2 column layout for side-by-side buttons
 
        cmds.showWindow()



        


#Menu Setup
class BG_Window(object):
    def __init__(self):
        self.materialsWindow=material_Window(self)#Initiates the material window (Doesnt load UI yet, done later on)

        #Window
        self.window = "BG_Window"
        self.title = ("City Generator")
        self.size = (1500, 800)

        if cmds.window(self.window, exists = True):#Checks if existing window is open
            cmds.deleteUI(self.window, window=True)#Closes existing window
        
        self.window = cmds.window(self.window, title=self.title,widthHeight=self.size)#Creates the window
        
        cmds.columnLayout(adjustableColumn = True)
        # title text
        cmds.text(self.title)
        # separator
        cmds.separator(height=20)
        
        cmds.text( label='Group Name' )
        self.inpBuildingGroup = cmds.textField(text="Buildings")
        self.buildingGroup=cmds.textField(self.inpBuildingGroup,query=True,text=True)
        
        #create layout
        cmds.columnLayout(adjustableColumn = True)
        self.inpLayoutMode = cmds.optionMenu( label='Layout mode',width=200)#Creates the dropdown menu for the layout mode options
        cmds.menuItem(label='Uniform with spacing variation') #Layout mode option for grid layout with some random leeway (Best looking one)
        cmds.menuItem(label='Uniform')#Layout mode option for grid layout
        cmds.menuItem(label='Random')#Layout mode option for entirely random positions
        cmds.separator(height=20)


        #Var inputs
        self.inpBuildingRange = cmds.floatFieldGrp( numberOfFields=2, label='Building distance range:', value1=-1000, value2=1000)
        self.inpBuildingHeight = cmds.floatFieldGrp( numberOfFields=2, label='Building Height range:', value1=10, value2=100)
        self.inpBuildingWidth = cmds.floatFieldGrp( numberOfFields=2, label='Building Width range:', value1=10, value2=20)
        self.inpBuildingDepth = cmds.floatFieldGrp( numberOfFields=2, label='Building Depth range:', value1=10, value2=20)
        self.inpNoBuildings = cmds.intSliderGrp(field=True, label='Number of buildings:', minValue=1,maxValue=5000, value=1000)
        cmds.separator(height=20)

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

        self.inpEffectapplyMaterial=cmds.checkBox(label='Auto UV and apply material(s) to buildings',onCommand=self.materialsWindow.createMaterialUI)#Doesn't have a chance input because it will always happen on all buildings if selected
        
        cmds.separator(style='none')#Resets the layout to one after the other
        cmds.columnLayout(adjustableColumn = True)

        #Gen button
        self.buildBtn = cmds.button( label='Create Buildings', command=self.genBuildings,width=500)
        self.undoBtn = cmds.button( label='Undo Last City', command=self.removeBuildings,width=500)
        self.randomiseBtn = cmds.button( label='Randomize all values', command=self.randomiseValues,width=500)
        self.resetBtn = cmds.button( label='Reset all values to defaults', command=self.resetValues,width=500)



        cmds.showWindow()





    def toggleSliderLock(self,slider,*args):#Toggles a slider bar (Needs to be a function as it's called before the UI elements being toggled are made)
        if  cmds.intSliderGrp(slider,query=True,enable=True):#If slider is enabled
            print("Disabling slider",slider)
            cmds.intSliderGrp(slider,edit=True,enable=False)#Disable it
        elif cmds.intSliderGrp(slider,query=True,enable=False):#If slider is disabled
            cmds.intSliderGrp(slider,edit=True,enable=True)#Enable it
            print("Enabling slider",slider)
        else:
            cmds.intSliderGrp(slider,edit=True,enable=True)#Enable it
            print("Enabling slider",slider)

    def removeBuildings(self, *args):#Removes the last generated city (Whichever name is stored in self.buildinggroup)
        try:
            cmds.delete(self.buildingGroup) #Deletes the buildings group
            cmds.delete("Ground_Plane") #Deletes the ground plane
        except ValueError:#Catches in case the user has deleted one or more of these elements
            pass#Does nothing but an except needs to do "something" so this is here

    def useEffect(self,effectChance):#Returns true or false on whether or not to apply an effect based on its' inputted likelyhood
        useVal=randInteger(1,100)#Produces a random value between 1 and 100
        if useVal<=effectChance:#If the random val is within the range of 0-effectChance
            return True
        else:
            return False

    def randomiseValues(self,*args):
        #Randomizes the height width and depth
        buildingRangeMin=randInteger(10,100)#Sets the lower bound as a var so upper cant be smaller than lower
        cmds.floatFieldGrp(self.inpBuildingHeight, edit=True, value1=buildingRangeMin)#Updates the value to a random one
        cmds.floatFieldGrp(self.inpBuildingHeight, edit=True, value2=randInteger(buildingRangeMin,100))#Updates the value to a random one

        buildingRangeMin=randInteger(10,100)#Sets the lower bound as a var so upper cant be smaller than lower
        cmds.floatFieldGrp(self.inpBuildingWidth, edit=True, value1=buildingRangeMin)#Updates the value to a random one
        cmds.floatFieldGrp(self.inpBuildingWidth, edit=True, value2=randInteger(buildingRangeMin,100))#Updates the value to a random one
        
        buildingRangeMin=randInteger(10,100)#Sets the lower bound as a var so upper cant be smaller than lower
        cmds.floatFieldGrp(self.inpBuildingDepth, edit=True, value1=buildingRangeMin)#Updates the value to a random one
        cmds.floatFieldGrp(self.inpBuildingDepth, edit=True, value2=randInteger(buildingRangeMin,100))#Updates the value to a random one        

        cmds.intSliderGrp(self.inpNoBuildings, edit=True, value=randInteger(5,5000))#Randomizes the number of buildings and updates the slider input box

        #Randomizes the effects and their likeliness
        checkBoxBool=random.choice([True, False])#Picks a true or false value for the effect (Is a var so it can sync with the slider lock)
        cmds.checkBox(self.inpEffectAddWindows, edit=True, value=checkBoxBool)#Edits the checkbox to the random bool
        cmds.intSliderGrp(self.inpEffectAddWindowsChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))
        
        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectBevel, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectBevelChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectScaleTop, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectScaleTopChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectRotate, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectRotateChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

    def resetValues(self,*args):#Resets all values to their defaults
        cmds.floatFieldGrp(self.inpBuildingHeight, edit=True, value1=10,value2=100)#Updates the value to a random one
        cmds.floatFieldGrp(self.inpBuildingWidth, edit=True, value1=10,value2=20)#Updates the value to a random one        
        cmds.floatFieldGrp(self.inpBuildingDepth, edit=True, value1=10,value2=20)#Updates the value to a random one

        cmds.intSliderGrp(self.inpEffectAddWindowsChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.intSliderGrp(self.inpEffectBevelChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.intSliderGrp(self.inpEffectScaleTopChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.intSliderGrp(self.inpEffectRotateChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.optionMenu(self.inpLayoutMode,edit=True,value="Uniform with spacing variation")#Updates the optionMenu with a random choice from the list


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
        createdBuildings=0#Counter of buildings finished generating used for the progressWindow to live update with the generation
        self.windowBuildings=[]#An array of buildings with window geometry so the material can be different to non-window buildings
        self.bevelBuildings=[]#An array of buildings with bevels applied so different faces can be selected for the roof mats
        print("Building Materials",self.materialsWindow.buildingMaterials)
        print("Glass Materials",self.materialsWindow.glassMaterials)


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
        if cmds.checkBox(self.inpEffectapplyMaterial, query=True, value=True):#Queries if check box is checked
            effects.append(["applyMaterial",100])#Adds the effect to the list of effects to use (And a 100% likelihood so all buildings are material-ed)

        #main loop
        self.buildingGroup=cmds.textField(self.inpBuildingGroup,query=True,text=True)
        if cmds.objExists(self.buildingGroup):
            cmds.confirmDialog(title="Warning!",message=("A group named "+self.buildingGroup+" already exists, generated buildings will be placed into it"))
        else:
            cmds.group(empty=True, name=self.buildingGroup)#Creates the group that the buildings will be placed into
        
        print("Layout Mode:",layoutMode)
        cmds.progressWindow(endProgress=1)#Removes any existing progress windows from past runs
        self.progressWindow=cmds.progressWindow(title="City Generation Progress",status="City Generation Progress",isInterruptable=1,maxValue=valNoBuildings)#,steps=100/valNoBuildings)#Starts the (invisible) progressWindow, used to catch the ESC key to exit
        for buildingNo in range(1,valNoBuildings+1):#Plus 1 so first building is building 1 but still exact range

            cmds.progressWindow(self.progressWindow,edit=True, step=1, status=("Finished "+str(buildingNo)+"/"+str(valNoBuildings)+" buildings"))#Starts the (invisible) progressWindow, used to catch the ESC key to exit
            if cmds.progressWindow(self.progressWindow,query=1, isCancelled=1):
                break
            buildingName=(self.buildingGroup+"_Building_"+str(buildingNo))#Names the buildings in the format Building_1

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
            try:
                cmds.xform(buildingName,translation=buildingPosition,worldSpace=True,centerPivots=True,absolute=True)#Moves the building to the generated position
            except ValueError as e:
                print(e)
                cmds.confirmDialog(title="Error!",message=("A building named "+buildingName+" already exists, generation stopped. Choose a new group name and retry."))
                break

        #Applies effects to current building

            for effectData in effects: #Loops through each piece of data in the 2d array (Array contains the effect name and then its % chance fof being applied)
                effect=effectData[0]
                effectChance=effectData[1]

                if self.useEffect(effectChance)==True:#If it's selected to use the effect
                    addBuildingEffects(self,effect,buildingName)#Apply the effect
            cmds.parent(buildingName,self.buildingGroup)
            createdBuildings+=1 #increments the counter for the status bar by 1
            print("\n")
            
        cmds.progressWindow(self.progressWindow,endProgress=1)

print("\n"*30)
print("Starting...")
#Main startup
myWindow = BG_Window()