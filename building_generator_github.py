#Maya City Generator - Callum Stuart, Birmingham City University Visual Effects
import maya.cmds as cmds
import maya.mel as mel
import random

layoutMode=""

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
        cmds.scale(randFloat(0.7,1.3),randFloat(0.7,1.3),1)
    
    elif effect=="addTower":#Scale top in
        cmds.select(buildingName+'.e[30:34]')
        cmds.select(buildingName+'.e[25:29]',add=True)
        cmds.scale(randFloat(0.5,1.5),randFloat(0.5,1.5),1)

    elif effect=="bevel":#Bevels edges
        edgeRingVal=randInteger(0,130)#Picks the edge (ring) to bevel        
        cmds.polyBevel(buildingName+".e[25:29]", offset=randFloat(0.1,0.9),offsetAsFraction=True )
        self.bevelBuildings.append(buildingName)#USed for the texture effect so it knows which buildings to add different glass mats to

    elif effect=="rotate":#Rotates the building along the Y axis only
        cmds.select(buildingName,hierarchy=True)#Selects the building AND children (Else children aren't rotated)
        rotateVal=(0,randFloat(5,355),0)#Gets a random val (range is 5-355 so the rotation is always noticable)
        cmds.xform(buildingName,rotation=rotateVal,worldSpace=True,centerPivots=True,absolute=True)#Rotates the building

    elif effect=="addBalcony":#Adds a balcony(s) to the side of the building
        midEdges=[5,10,15,20]
        balconyYpositions=[]

        for edge in midEdges:#Loops through each of the edges that dont touch the ground or the top of the building            
            balconyYpositions.append(cmds.xform(buildingName+".e["+str(edge)+"]",query=True,worldSpace=True,translation=True)[1])#Adds the Y coordinate of the edge to be used as a possible Y coord for the balcony

        noBalconies=randInteger(1,16)#Randomly picks a number of balconies to add
        for balconyCount in range(0,noBalconies):
            balconyName=(buildingName+"_Balcony_"+str(balconyCount))
            cmds.polyCube(width=self.buildingWidth/3,height=self.buildingHeight/100,depth=self.buildingDepth/3,name=balconyName,subdivisionsX=5,subdivisionsY=5, subdivisionsZ=5)#Creates the cube to be morphed into a balcony
            
            cmds.polyExtrudeFacet(balconyName+".f[25]",balconyName+".f[35]",balconyName+".f[45]",balconyName+".f[47]",balconyName+".f[49]",balconyName+".f[39]",balconyName+".f[29]",balconyName+".f[27]",kft=False, ltz=1.5, ls=(1, 1, 0),smoothingAngle=45)#Extrudes the faces upwards to make a balcony
            balconyAxis=random.choice(["X+","Z+","X-","Z-"])#Chooses whether to place the balcony on the X or Z axis
            if balconyAxis=="X+":
                balconyPosition=[self.buildingPosition[0]+(self.buildingWidth/2),random.choice(balconyYpositions),self.buildingPosition[2]]
            elif balconyAxis=="Z+":
                balconyPosition=[self.buildingPosition[0],random.choice(balconyYpositions),self.buildingPosition[2]+(self.buildingDepth/2)]
            elif balconyAxis=="X-":
                balconyPosition=[self.buildingPosition[0]-(self.buildingWidth/2),random.choice(balconyYpositions),self.buildingPosition[2]]
            elif balconyAxis=="Z-":
                balconyPosition=[self.buildingPosition[0],random.choice(balconyYpositions),self.buildingPosition[2]-(self.buildingDepth/2)]
           
            cmds.xform(balconyName,translation=balconyPosition,worldSpace=True,centerPivots=True,absolute=True)#Moves the balcony to the position based on the chosen axis
            cmds.parent(balconyName,buildingName)#Parents the balcony to the building (Mostly for organization)
        self.balconyBuildings.append(buildingName)#Adds the building into a list used for handling textures

    elif effect=="addHeliPad":
        heliPadName=(buildingName+"_helipad_1")
        cmds.polyCylinder( subdivisionsX=8, subdivisionsY=2, subdivisionsZ=2, height=0.5,radius=2,name=heliPadName)
        cmds.xform(heliPadName,translation=[(self.buildingPosition[0]+3),self.buildingHeight,(self.buildingPosition[2]-3)],rotation=[0,randInteger(1,359),0])
        cmds.parent(heliPadName,buildingName)#Parents the helipad to the building (Mostly for organization)
        self.heliPadBuildings.append(buildingName)#Adds the building into a list used for handling textures
    
    elif effect=="addBillboard":
        billboardName=(buildingName+"_billboard_1")
        cmds.polyCube( subdivisionsX=5, subdivisionsY=4, subdivisionsZ=4,name=billboardName,width=5,height=3,depth=0.5)
        cmds.polyExtrudeFacet(billboardName+".f[64]",billboardName+".f[60]",billboardName+".f[75]",billboardName+".f[79]",kft=False, ltz=10, ls=(1, 1, 0),smoothingAngle=45)#Extrudes the faces upwards to make a balcony
        if buildingName in self.windowBuildings:#checks if the building has windows as the billboard needs a slightly different rotation to prevent clipping
            cmds.xform(billboardName,translation=[(self.buildingPosition[0]-self.buildingWidth*0.25),(self.buildingHeight+randInteger(3,10)),(self.buildingPosition[2]-self.buildingDepth*0.2)],rotation=[0,randInteger(-45,-30),0])
        else:#Regular range of rotation
            cmds.xform(billboardName,translation=[(self.buildingPosition[0]-self.buildingWidth*0.25),(self.buildingHeight+randInteger(3,10)),(self.buildingPosition[2]-self.buildingDepth*0.2)],rotation=[0,randInteger(-45,0),0])
        cmds.parent(billboardName,buildingName)#Parents to the building (Mostly for organization)
        self.billboardBuildings.append(buildingName)#Adds the building into a list used for handling textures

    elif effect=="placeUneven":#Checks that the effect hasnt been disabled
        if self.unevenTerrainExists==True:#Variable used to skip this effect if the terrain doesn't exist
            try:
                terrain=cmds.textField(self.inpPlaceUnevenTerrain,query=True,text=True)#Gets the terrain name from the user input box
                print("Terrain:",terrain)
                aimLocator = cmds.spaceLocator(n='aimloc',a=True)[0]#Locator used to get the position
                closest = cmds.createNode('closestPointOnMesh')#Creates the node used to get the position
                terrain_sh = cmds.listRelatives(terrain, noIntermediate=True)[0]
                cmds.connectAttr(terrain_sh+'.worldMesh[0]', closest+'.inMesh')
                cmds.connectAttr(terrain_sh+'.worldMatrix[0]', closest+'.inputMatrix')
                cmds.connectAttr(buildingName+'.t', closest+'.inPosition')        
                cmds.select(terrain, aimLocator)
                pctr = mel.eval('pointOnPolyConstraint -offset 0 0 0  -weight 1;')[0]#Uses MEL instead of python because of a python bug when running this command
                cmds.connectAttr('{}.parameterU'.format(closest), '{}.target[0].targetU'.format(pctr), f=True)
                cmds.connectAttr('{}.parameterV'.format(closest), '{}.target[0].targetV'.format(pctr), f=True)
                cmds.orientConstraint(aimLocator, buildingName, mo=False, weight=1)
                cmds.xform(buildingName,translation=[cmds.getAttr('aimloc.translateX'),(cmds.getAttr('aimloc.translateY')+self.buildingHeight/3),cmds.getAttr('aimloc.translateZ')],rotation=[cmds.getAttr('aimloc.rotateX'),cmds.getAttr('aimloc.rotateY'),cmds.getAttr('aimloc.rotateZ')])#Translates the building to the new pos on the terrain
                cmds.delete("aimloc")#Deletes the aim locator
                self.unevenTerrainExists=True
            except (ValueError, TypeError):
                self.unevenTerrainExists=False#Toggles the boolean so this doesn't pop up for each building
                cmds.confirmDialog(title="Error!",message=("Terrain named "+terrain+" does not exist. Effect has been disabled."))#Error popup
                cmds.delete("aimloc")#Deletes the aim locator



    elif effect=="applyMaterial":#Effect to add materials from a predetermined list to specific parts of building geometry. Has to be last so all geometry is there
        uvScale=cmds.floatSliderGrp(self.inpUVScale,query=True, value=True)#Gets the scale factor from the slider
        cmds.polyAutoProjection(buildingName+".f[*]", layoutMethod=0, insertBeforeDeformers=1, createNewMap=0, layout=0, sc=2, o=0, p=6, ps=0.2, ws=0,scale=(uvScale,uvScale,uvScale) )#Performs an automatic UV on the building
        
        #Assigns main building textures
        if len(self.materialsWindow.buildingMaterials)>0:#Checks to make sure there's something in the list else the random lib crashes
            randomMatBuilding=random.choice(self.materialsWindow.buildingMaterials)
            print("Assigning ",randomMatBuilding,"as the glass mat for",buildingName)
            cmds.sets(forceElement=randomMatBuilding)#Assigns a random material from the array to the selected object (A building)

            #Assigns balcony textures (Only after assigning main building texture to ensure all conditions to texture are met)
            print("Balcony Buildings",self.balconyBuildings)
            if buildingName in self.balconyBuildings and len(self.materialsWindow.buildingMaterials)>0:#Checks to make sure there's something in the list else the random lib crashes
                for balconyName in cmds.ls(objectsOnly=True):#Loops through all objects in the scene
                    if buildingName in balconyName and "Balcony" in balconyName:
                        print("Balcony Name",balconyName)
                        cmds.polyAutoProjection(balconyName+".f[*]", layoutMethod=0, insertBeforeDeformers=1, createNewMap=0, layout=0, sc=2, o=0, p=6, ps=0.2, ws=0,scale=(uvScale,uvScale,uvScale) )#Performs an automatic UV on the balcony
                        cmds.select(balconyName)#Selects the balcony by its name
                        cmds.sets(forceElement=randomMatBuilding)#Apply the same texture to the balcony as the main building
                        cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)
            elif buildingName in self.balconyBuildings and len(self.materialsWindow.billboardMaterials)==0:#If there are no materials
                cmds.polyAutoProjection(balconyName+".f[*]", layoutMethod=0, insertBeforeDeformers=1, createNewMap=0, layout=0, sc=2, o=0, p=6, ps=0.2, ws=0,scale=(uvScale,uvScale,uvScale) )#Performs an automatic UV on the balcony



        #Assigns window textures
        if buildingName in self.windowBuildings and len(self.materialsWindow.glassMaterials)>0:#If the selected buildings has had the addWindows effect applied. Checks to make sure there's something in the list else the random lib crashes
            randomMatGlass=random.choice(self.materialsWindow.glassMaterials)
            print("Assigning ",randomMatGlass,"as the glass mat for",buildingName)

            if buildingName in self.bevelBuildings and buildingName in self.windowBuildings:
                cmds.select(buildingName+'.f[45:74]',buildingName+'.f[0:24]',buildingName+'.f[95:144]')#Selects different faces if the building is also beveled
            else:
                cmds.select(buildingName+'.f[50:74]',buildingName+'.f[0:24]',buildingName+'.f[95:149]')#Select the faces of the windows
            cmds.sets(forceElement=randomMatGlass)#Apply a random glass material
            cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)

        #Assigns helipad textures
        if buildingName in self.heliPadBuildings and len(self.materialsWindow.heliPadMaterials)>0:#If the selected buildings has had the addWindows effect applied. Checks to make sure there's something in the list else the random lib crashes            
            randomMatHeliPad=random.choice(self.materialsWindow.heliPadMaterials)
            print("Assigning ",randomMatHeliPad,"as the helipad mat for",buildingName)
            heliPadName=(buildingName+"_helipad_1")            
            cmds.select(heliPadName)#Selects the balcony by its name
            cmds.sets(forceElement=randomMatHeliPad)#Apply the same texture to the balcony as the main building
            cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)

       #Assigns billboard textures
        if buildingName in self.billboardBuildings and len(self.materialsWindow.billboardMaterials)>0:#If the selected buildings has had the addWindows effect applied. Checks to make sure there's something in the list else the random lib crashes            
            randomMatbillboard=random.choice(self.materialsWindow.billboardMaterials)
            print("Assigning ",randomMatbillboard,"as the billboard mat for",buildingName)
            billboardName=(buildingName+"_billboard_1")            
            cmds.select(billboardName)#Selects the billboard by its name
            cmds.sets(forceElement=randomMatbillboard)#Apply the same texture to the balcony as the main building
            cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)
        elif buildingName in self.billboardBuildings and len(self.materialsWindow.billboardMaterials)==0:#If there are no materials
            cmds.polyAutoProjection(billboardName+".f[*]", layoutMethod=0, insertBeforeDeformers=1, createNewMap=0, layout=2, sc=1, o=1, p=6, ps=0.2, ws=0,scale=(uvScale,uvScale,uvScale) )#Performs an automatic UV on the billboard


        #Assigns roof textures
        if len(self.materialsWindow.roofMaterials)>0:#Checks to make sure there's something in the list else the random lib crashes
            randomMatRoof=random.choice(self.materialsWindow.roofMaterials)
            print("Assigning ",randomMatRoof,"as the roof mat for",buildingName)
            
            if buildingName in self.bevelBuildings and buildingName in self.windowBuildings:
                cmds.select(buildingName+'.f[537:541]',buildingName+'.f[25:44]')#Select the faces of the roof (When beveled and windows added)
            elif buildingName in self.bevelBuildings and buildingName not in self.windowBuildings:
                cmds.select(buildingName+'.f[150:154]',buildingName+'.f[20:39]')#Select the faces of the roof (When beveled)                
            else:
                cmds.select(buildingName+'.f[25:49]')#Select the faces of the roof (When flat)
            cmds.sets(forceElement=randomMatRoof)#Apply a random roof material
            cmds.select(buildingName)#Select the entire building object (Else this carries over to the next building)








#main-------------------------------------------------
class material_Window(object):#Class for the wiondows to do with the material selections

    def addMaterial(self,window,matList,TSList,*args):#Function used to add new materials to the given list (And updates all global material lists)
        print(self,window,matList,TSList)
        newMatList=matList+(cmds.textScrollList(self.sceneMaterialsTS, query=True, si=True))#Concats the original list and the user's selections into one list
        newMatList=list(dict.fromkeys(newMatList))#Converts the material list into a dictionary and back to remove duplicates
        cmds.textScrollList(TSList,edit=True,removeAll=True,append=newMatList)#Clears the existing list then appends the new array

        #Updates the lists so the main class can access them
        if cmds.textScrollList(self.buildingMaterialsTSList, query=True, allItems=True) != None:#Checks if the list returns NONE becaise it's empty (This breaks everything and has annoyed me for about a day)
            self.buildingMaterials=cmds.textScrollList(self.buildingMaterialsTSList, query=True, allItems=True)
        
        if cmds.textScrollList(self.glassMaterialsTSList, query=True, allItems=True) != None:
            self.glassMaterials=cmds.textScrollList(self.glassMaterialsTSList, query=True, allItems=True)

        if cmds.textScrollList(self.roofMaterialsTSList, query=True, allItems=True) != None:
            self.roofMaterials=cmds.textScrollList(self.roofMaterialsTSList, query=True, allItems=True)

        if cmds.textScrollList(self.heliPadMaterialsTSList, query=True, allItems=True) != None:
            self.heliPadMaterials=cmds.textScrollList(self.heliPadMaterialsTSList, query=True, allItems=True)

        if cmds.textScrollList(self.billboardMaterialsTSList, query=True, allItems=True) != None:
            self.billboardMaterials=cmds.textScrollList(self.billboardMaterialsTSList, query=True, allItems=True)

        #Prints the materials to the script editor for testing
        print("Building Materials",self.buildingMaterials)
        print("Glass Materials",self.glassMaterials)
        print("Roof Materials",self.roofMaterials)
        print("HeliPad Materials",self.heliPadMaterials)
        print("Billboard Materials",self.billboardMaterials)



    def clearMaterialList(self,window,TSList,matList,*args):
        print("Clearing ",TSList)
        cmds.textScrollList(TSList,edit=True,removeAll=True)
        matList=matList.clear()

    def __init__(self,*args):
        #Creates the objects lists (Done in the init so they don't reset when the UI is re-opened, innit?)
        self.buildingMaterials=[]
        self.glassMaterials=[]
        self.roofMaterials=[]
        self.heliPadMaterials=[]
        self.billboardMaterials=[]



    def createMaterialUI(self,*args):#Creates and opens the window (Not in init so can be called seperately to creating the object)

        self.window="Material List"
        self.title = "Material List"
        self.size = (1500, 800)

        self.materialListWindow=cmds.window(title='Materials List', width=200)

        cmds.columnLayout(rowSpacing=10, columnWidth=200)
        cmds.text("Scene Materials",font="boldLabelFont")
        cmds.text("Select the desired shader groups from the list below (CTRL/Shift select for multiple) \n Click the button to add them to the wanted group \n All changes are saved automatically, so this window can be closed at any time",align="left")
        sceneMaterialsList = cmds.ls(set=True)#Gets all materials (sets) in the scene
        self.sceneMaterialsTS=cmds.textScrollList(append=sceneMaterialsList,allowMultiSelection=True) #Shows all materials in the scene as a textScrollList
        
        cmds.rowColumnLayout(numberOfRows=4)#Changes to a 2 column layout for side-by-side buttons
        cmds.text( label='Building Materials',font="boldLabelFont")#Title for this section
        self.buildingMaterialsTSList=cmds.textScrollList('Building Materials', append=self.buildingMaterials) 
        buildingMaterialsAppendButton=cmds.button( label='Add to Building Material list', command=lambda x: self.addMaterial(self,self.buildingMaterials,self.buildingMaterialsTSList))#Button to add selections to the list
        buildingMaterialsClearButton=cmds.button("Clear Building Material list",command=lambda x:self.clearMaterialList(self,self.buildingMaterialsTSList,self.buildingMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list
      

        cmds.text( label='Glass Materials',font="boldLabelFont" )#Title for this section
        self.glassMaterialsTSList=cmds.textScrollList('Glass Materials', append=self.glassMaterials) 
        glassMaterialsAppendButton=cmds.button( label='Add to Glass Materials list', command=lambda x: self.addMaterial(self,self.glassMaterials,self.glassMaterialsTSList))#Button to add selections to the list
        glassMaterialsClearButton=cmds.button("Clear Glass Materials list",command=lambda x:self.clearMaterialList(self,self.glassMaterialsTSList,self.glassMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list
 
        cmds.text( label='Roof Materials',font="boldLabelFont" )#Title for this section
        self.roofMaterialsTSList=cmds.textScrollList('Roof Materials', append=self.roofMaterials) 
        roofMaterialsAppendButton=cmds.button( label='Add to Roof Materials list', command=lambda x: self.addMaterial(self,self.roofMaterials,self.roofMaterialsTSList))#Button to add selections to the list
        roofMaterialsClearButton=cmds.button("Clear Roof Materials list",command=lambda x:self.clearMaterialList(self,self.roofMaterialsTSList,self.roofMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list
 
        cmds.text( label='Helicopter Pad Materials',font="boldLabelFont" )#Title for this section
        self.heliPadMaterialsTSList=cmds.textScrollList('Helicopter Pad Materials', append=self.heliPadMaterials) 
        heliPadAppendButton=cmds.button( label='Add to Heli-Pad Materials list', command=lambda x: self.addMaterial(self,self.heliPadMaterials,self.heliPadMaterialsTSList))#Button to add selections to the list
        heliPadClearButton=cmds.button("Clear Heli-Pad Materials list",command=lambda x:self.clearMaterialList(self,self.heliPadMaterialsTSList,self.heliPadMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list

        cmds.text( label='Billboard Materials',font="boldLabelFont" )#Title for this section
        self.billboardMaterialsTSList=cmds.textScrollList('Billboard Materials', append=self.billboardMaterials) 
        billboardAppendButton=cmds.button( label='Add to billboard Materials list', command=lambda x: self.addMaterial(self,self.billboardMaterials,self.billboardMaterialsTSList))#Button to add selections to the list
        billboardClearButton=cmds.button("Clear billboard Materials list",command=lambda x:self.clearMaterialList(self,self.billboardMaterialsTSList,self.billboardMaterials))#Removes all items then appends the new array (Helps prevent duplicates))#Button to clear the list


        
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
        cmds.separator(height=20,style="shelf")
        cmds.text( label='Group Name',align="left" )
        self.inpBuildingGroup = cmds.textField(text="Buildings",statusBarMessage="The name of the group to be created that the buildings will be placed into")#Text input for the group name that the buildings are placed into
        self.updateGroupName()#Updates the group name and removes any illegal characters
        #create layout
        cmds.columnLayout(adjustableColumn = True)
        self.inpLayoutMode = cmds.optionMenu( label='Layout mode',width=200,statusBarMessage="The mode used to decide where to place the buildings")#Creates the dropdown menu for the layout mode options
        cmds.menuItem(label='Uniform with spacing variation') #Layout mode option for grid layout with some random leeway (Best looking one)
        cmds.menuItem(label='Uniform (Grid)')#Layout mode option for grid layout
        cmds.menuItem(label='Random')#Layout mode option for entirely random positions
        cmds.separator(height=20,style="shelf")


        #Var inputs
        self.inpBuildingRange = cmds.floatFieldGrp(columnAlign=[1,"left"], numberOfFields=2, label='City range/row width:', value1=-1000, value2=1000)
        self.inpBuildingHeight = cmds.floatFieldGrp(columnAlign=[1,"left"], numberOfFields=2, label='Building Height range:', value1=10, value2=100)
        self.inpBuildingWidth = cmds.floatFieldGrp(columnAlign=[1,"left"], numberOfFields=2, label='Building Width range:', value1=10, value2=20)
        self.inpBuildingDepth = cmds.floatFieldGrp(columnAlign=[1,"left"], numberOfFields=2, label='Building Depth range:', value1=10, value2=20)
        self.inpNoBuildings = cmds.intSliderGrp(columnAlign=[1,"left"], width=1000, field=True, label='Number of buildings:', minValue=1,maxValue=5000, value=1000)
        cmds.separator(height=20,style="shelf")

        #Effect Tickboxes and sliders
        cmds.rowColumnLayout(nc=2,columnWidth=[(1, 300), (2, 1000)])#Changes the layout so can have 2 items next to each other
        self.inpEffectAddWindows=cmds.checkBox(label='Add Windows',changeCommand=lambda x: self.toggleSliderLock(self.inpEffectAddWindowsChance),statusBarMessage="Adds windows to the buildings by extruding faces inwards")#Checkbox for toggling the effect. Lambda is used to define the changecommand without actually running it, so a variable can be passed and the one function can manage all slider toggles
        self.inpEffectAddWindowsChance = cmds.intSliderGrp(width=10,columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        
        self.inpEffectBevel=cmds.checkBox(label='Bevel Top edges',changeCommand=lambda x: self.toggleSliderLock(self.inpEffectBevelChance),statusBarMessage="Bevels one of the top edges of the building")
        self.inpEffectBevelChance = cmds.intSliderGrp(columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectScaleTop=cmds.checkBox(label='Scale Top Edges', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectScaleTopChance),statusBarMessage="Scales the top of the building inwards or outwards so it isn't a perfect oblong")
        self.inpEffectScaleTopChance = cmds.intSliderGrp(columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectRotate=cmds.checkBox(label='Rotate building', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectRotateChance),statusBarMessage="Rotates the building around the Y axis")
        self.inpEffectRotateChance = cmds.intSliderGrp(columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectAddBalcony=cmds.checkBox(label='Add balconies', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectAddBalconyChance),statusBarMessage="Creates and places a seperate piece of geometry on the building which looks like a balcony \n (Only placed along the edge loops)")
        self.inpEffectAddBalconyChance = cmds.intSliderGrp(columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectAddHeliPad=cmds.checkBox(label='Add Helicopter Landing Pads', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectAddHeliPadChance),statusBarMessage="Creates and places a heli-pad on the roof of the building")
        self.inpEffectAddHeliPadChance = cmds.intSliderGrp(columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectAddBillboard=cmds.checkBox(label='Add Billboards', changeCommand=lambda x: self.toggleSliderLock(self.inpEffectAddBillboardChance),statusBarMessage="Creates and places a billboard on the roof of the building")
        self.inpEffectAddBillboardChance = cmds.intSliderGrp(columnAlign=[1,"left"],field=True, label='% likelihood:', minValue=1,maxValue=100, value=50,enable=False)

        self.inpEffectapplyMaterial=cmds.checkBox(label='Auto UV and apply material(s) to buildings',changeCommand=lambda x: self.toggleSliderLock(self.inpUVScale),statusBarMessage="Performs an automatic UV on the building and all extra elements, then applies a random material from the lists in the material management window")#Doesn't have a chance input because it will always happen on all buildings if selected
        self.inpUVScale=cmds.floatSliderGrp(columnAlign=[1,"left"],field=True, label='UV Scale:', minValue=0.5,maxValue=10, value=5,enable=False)

        self.inpEffectPlaceUneven=cmds.checkBox(label='Place buildings across uneven terrain',changeCommand=lambda x: self.toggleSliderLock(self.inpPlaceUnevenTerrain),statusBarMessage="Places buildings along the uneven surface defined in the input box")#Doesn't have a chance input because it will always happen on all buildings if selected
        self.inpPlaceUnevenTerrain=cmds.textField(text="Terrain Name",enable=False)
        
        cmds.columnLayout(adjustableColumn = False,columnWidth=1500)

        cmds.separator(style='none',height=50)

        self.buildBtn = cmds.button( label='Create Buildings', command=self.genBuildings,width=300,statusBarMessage="Generates a city using the specified options")#generation button
        self.undoBtn = cmds.button( label='Undo Last City', command=self.removeBuildings,width=300,statusBarMessage="Undo's the last city with the name currently in the group name box.")#undo button
        cmds.separator(style='none',height=20)
        self.randomiseBtn = cmds.button( label='Randomize all values', command=self.randomiseValues,width=300,statusBarMessage="Randomizes the effects and their associated values")
        self.resetBtn = cmds.button( label='Reset all values to defaults', command=self.resetValues,width=300,statusBarMessage="Resets the values to the defaults")
        cmds.separator(style='none',height=20)
        self.materialsBtn=cmds.button(label="Open Material Management Window",command=self.materialsWindow.createMaterialUI,width=300,statusBarMessage="Opens the window used to specify materials to different elements of the buildings")



        cmds.showWindow()


    def updateGroupName(self,*args):#Updates the group name variable and removes illegal characters
        self.buildingGroup=cmds.textField(self.inpBuildingGroup,query=True,text=True)#Updates the buildingGroup name
        illegalChars=['~', ':', "'", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`', '}', '.', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/'," ","£"]#List of characters to be replaced
        for illegal in illegalChars:#Loops through every illegal character in the above array
            self.buildingGroup=self.buildingGroup.replace(illegal,"_")#Replaces any instances of the current illegal character with an underscore


    def toggleSliderLock(self,slider,*args):#Toggles a slider bar (Needs to be a function as it's called before the UI elements being toggled are made)
        sliderType=1
        toggled=False
        while toggled==False:
            try:
                if sliderType==1:#First slider type is most likely
                    if  cmds.intSliderGrp(slider,query=True,enable=True):#If slider is enabled
                        print("Disabling slider",slider)
                        cmds.intSliderGrp(slider,edit=True,enable=False)#Disable it
                        toggled=True
                    elif cmds.intSliderGrp(slider,query=True,enable=False):#If slider is disabled
                        cmds.intSliderGrp(slider,edit=True,enable=True)#Enable it
                        print("Enabling slider",slider)
                        toggled=True
                    else:
                        cmds.intSliderGrp(slider,edit=True,enable=True)#Enable it
                        print("Enabling slider",slider)
                        toggled=True
                elif sliderType==2:#Second slider type (Float sliders)
                    if  cmds.floatSliderGrp(slider,query=True,enable=True):#If slider is enabled
                        print("Disabling slider",slider)
                        cmds.floatSliderGrp(slider,edit=True,enable=False)#Disable it
                        toggled=True
                    elif cmds.floatSliderGrp(slider,query=True,enable=False):#If slider is disabled
                        cmds.floatSliderGrp(slider,edit=True,enable=True)#Enable it
                        print("Enabling slider",slider)
                        toggled=True
                    else:
                        cmds.floatSliderGrp(slider,edit=True,enable=True)#Enable it
                        print("Enabling slider",slider)
                        toggled=True
                elif sliderType==3:#Third slider group (Text fields) (Not technically a slider but it's easier to call it one)
                    if  cmds.textField(slider,query=True,enable=True):#If slider is enabled
                        print("Disabling slider",slider)
                        cmds.textField(slider,edit=True,enable=False)#Disable it
                        toggled=True
                    elif cmds.textField(slider,query=True,enable=False):#If slider is disabled
                        cmds.textField(slider,edit=True,enable=True)#Enable it
                        print("Enabling slider",slider)
                        toggled=True
                    else:
                        cmds.textField(slider,edit=True,enable=True)#Enable it
                        print("Enabling slider",slider)
                        toggled=True

            except RuntimeError:#Errors because its looking for a different thing
                sliderType+=1
        


    def removeBuildings(self, *args):#Removes the last generated city (Whichever name is stored in self.buildinggroup)
        self.updateGroupName()
        if cmds.objExists(self.buildingGroup):
            cmds.delete(self.buildingGroup) #Deletes the buildings group
        else:
            cmds.confirmDialog(title="Error!",message=("A group named "+self.buildingGroup+" does not exist. No objects have been deleted."))


    def useEffect(self,effectChance):#Returns true or false on whether or not to apply an effect based on its' inputted likelyhood
        useVal=randInteger(1,100)#Produces a random value between 1 and 100
        if useVal<=effectChance:#If the random val is within the range of 0-effectChance
            return True
        else:
            return False

    def randomiseValues(self,*args):

        randomLayoutMode=random.choice(['Uniform with spacing variation',"Uniform (Grid)","Random"])#picks a random value from the layout mode list
        cmds.optionMenu(self.inpLayoutMode,edit=True,value=randomLayoutMode)#Updates the optionMenu with a random choice from the list

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
        cmds.checkBox(self.inpEffectAddWindows, edit=True, value=checkBoxBool)#Edits the checkbox to the random bool (So it stays in sync with the effect)
        cmds.intSliderGrp(self.inpEffectAddWindowsChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))#Randomizes the likelihood value
        
        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectBevel, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectBevelChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectScaleTop, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectScaleTopChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectRotate, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectRotateChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectAddBalcony, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectAddBalconyChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectAddHeliPad, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectAddHeliPadChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))

        checkBoxBool=random.choice([True, False])
        cmds.checkBox(self.inpEffectAddBillboard, edit=True, value=checkBoxBool)
        cmds.intSliderGrp(self.inpEffectAddBillboardChance,edit=True,enable=checkBoxBool,value=randInteger(1,100))


    def resetValues(self,*args):#Resets all values to their defaults
        cmds.floatFieldGrp(self.inpBuildingHeight, edit=True, value1=10,value2=100)#Updates the value to a random one
        cmds.floatFieldGrp(self.inpBuildingWidth, edit=True, value1=10,value2=20)#Updates the value to a random one        
        cmds.floatFieldGrp(self.inpBuildingDepth, edit=True, value1=10,value2=20)#Updates the value to a random one

        cmds.intSliderGrp(self.inpEffectAddWindowsChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectAddWindows,edit=True,value=False)#Turns off the check box
        
        cmds.intSliderGrp(self.inpEffectBevelChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectBevel,edit=True,value=False)#Turns off the check box
        
        cmds.intSliderGrp(self.inpEffectScaleTopChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectScaleTop,edit=True,value=False)#Turns off the check box
        
        cmds.intSliderGrp(self.inpEffectRotateChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectRotate,edit=True,value=False)#Turns off the check box
        
        cmds.intSliderGrp(self.inpEffectAddBalconyChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectAddBalcony,edit=True,value=False)#Turns off the check box
        
        cmds.intSliderGrp(self.inpEffectAddHeliPadChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectAddHeliPad,edit=True,value=False)#Turns off the check box
        
        cmds.intSliderGrp(self.inpEffectAddBillboardChance,edit=True, minValue=1,maxValue=100, value=50,enable=False)#Sliders default to off because the tickboxes also do
        cmds.checkBox(self.inpEffectAddBillboard,edit=True,value=False)#Turns off the check box
        

        cmds.optionMenu(self.inpLayoutMode,edit=True,value="Uniform with spacing variation")#Resets the layout mode to the default
        


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
        self.balconyBuildings=[]#An array of buildings with balconies applied (Need to be UV'd and textured seperately)
        self.heliPadBuildings=[]#An array of buildings with helipads applied (Need to be UV'd and textured seperately)
        self.billboardBuildings=[]#An array of buildings with billboards applied (Need to be UV'd and textured seperately)
        self.unevenTerrainExists=True#Boolean used to skip the unevenTerrain effect if the terrain doesn't exist
        print("Building Materials",self.materialsWindow.buildingMaterials)
        print("Glass Materials",self.materialsWindow.glassMaterials)


        self.effects=[]#Clears effects on each re-run
        
        #gets effects (In the order that works best to apply in)
        if cmds.checkBox(self.inpEffectScaleTop, query=True, value=True):#Queries if check box is checked
            self.effects.append(["scaleTop",cmds.intSliderGrp(self.inpEffectScaleTopChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectAddWindows, query=True, value=True):#Queries if check box is checked
            self.effects.append(["addWindows",cmds.intSliderGrp(self.inpEffectAddWindowsChance, query=True, value=True)])#Adds the effect and its % chance of being applied to an array
        if cmds.checkBox(self.inpEffectBevel, query=True, value=True):#Queries if check box is checked
            self.effects.append(["bevel",cmds.intSliderGrp(self.inpEffectBevelChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectAddBalcony, query=True, value=True):#Queries if check box is checked 
            self.effects.append(["addBalcony",cmds.intSliderGrp(self.inpEffectAddBalconyChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectAddHeliPad, query=True, value=True):#Queries if check box is checked 
            self.effects.append(["addHeliPad",cmds.intSliderGrp(self.inpEffectAddHeliPadChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectAddBillboard, query=True, value=True):#Queries if check box is checked 
            self.effects.append(["addBillboard",cmds.intSliderGrp(self.inpEffectAddBillboardChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectRotate, query=True, value=True):#Queries if check box is checked
            self.effects.append(["rotate",cmds.intSliderGrp(self.inpEffectRotateChance, query=True, value=True)])#Adds the effect to the list of effects to use
        if cmds.checkBox(self.inpEffectapplyMaterial, query=True, value=True):#Queries if check box is checked. addMaterial must be last so all geometry exists to texture
            self.effects.append(["applyMaterial",100])#Adds the effect to the list of effects to use (And a 100% likelihood so all buildings are material-ed)
        if cmds.checkBox(self.inpEffectPlaceUneven, query=True, value=True):#Queries if check box is checked. Sets the likelihood to 100% for this effect else the buildings are at different heights
            self.effects.append(['placeUneven',100])

        #main loop
        self.updateGroupName()
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
            self.buildingHeight=randFloat(valBuildingHeightMin,valBuildingHeightMax)
            self.buildingWidth=randFloat(valBuildingWidthMin,valBuildingWidthMax)
            self.buildingDepth=randFloat(valBuildingDepthMin,valBuildingDepthMax)

            cmds.polyCube(width=self.buildingWidth,height=self.buildingHeight,depth=self.buildingDepth,name=buildingName,subdivisionsX=5,subdivisionsY=5, subdivisionsZ=5)#Creates the cube to be morphed into a building


            #Generates the position for the building to be placed (Spawns at 0,0 by default)
            if layoutMode=="Random":#Randomly places buildings (May cause collisions)
                self.buildingPosition=[randFloat(valBuildingRangeMin,valBuildingRangeMax),self.buildingHeight/2,randFloat(valBuildingRangeMin,valBuildingRangeMax)] #Divs height by 2 because buildings are placed at 0 so half clips below
            
            elif layoutMode=="Uniform (Grid)":#Places buildings in a grid format with set spacing
                self.buildingPosition=[prevPosition,self.buildingHeight/2,zVal]
                prevPosition=prevPosition+(self.buildingWidth*2)
                if prevPosition*2>valBuildingRangeMax:#If the building goes out of range
                    prevPosition=valBuildingRangeMin#Resets the building to the left side
                    zVal=zVal+self.buildingDepth*3 #Starts placing buildings on the next row
            
            elif layoutMode=="Uniform with spacing variation":#Places buildings in a grid format with random (within range) spacing
                self.buildingPosition=[prevPosition,self.buildingHeight/2,zVal]
                prevPosition=prevPosition+(self.buildingWidth*randFloat(1.3,3.5))
                if prevPosition*2>valBuildingRangeMax:#If the building goes out of range
                    prevPosition=valBuildingRangeMin#Resets the building to the left side
                    zVal=zVal+self.buildingDepth*randFloat(2,3.5) #Starts placing buildings on the next row            
            try:
                cmds.xform(buildingName,translation=self.buildingPosition,worldSpace=True,centerPivots=True,absolute=True)#Moves the building to the generated position
            except ValueError as e:
                print(e)
                cmds.confirmDialog(title="Error!",message=("A building named "+buildingName+" already exists, generation stopped. Choose a new group name and retry."))
                break

        #Applies effects to current building

            for effectData in self.effects: #Loops through each piece of data in the 2d array (Array contains the effect name and then its % chance fof being applied)
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