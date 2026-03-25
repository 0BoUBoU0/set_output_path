bl_info = {
    "name": "Set Output Path",
    "author": "Yannick 'BoUBoU' Castaing",
    "description": "This addon will set your render output in the same location where your file is.",
    "location": "PROPERTIES > RENDER PANEL > OUTPUT PANEL",
    "doc_url": "",
    "warning": "",
    "category": "Render",
    "blender": (2, 90, 0),
    "version": (2,1,3)
}


'''

ajouter un custom field from script : 

        # use a user script if wanted
        if bpy.context.scene.campanprops.playblast_postscript_prop != None: 
            # update last version of the script
            post_script = bpy.context.scene.campanprops.playblast_postscript_prop
            post_script_name = post_script.name
            post_script_filepath = post_script.filepath

            bpy.data.texts.remove(post_script)
            bpy.ops.text.open(filepath=post_script_filepath)
            bpy.context.scene.campanprops.playblast_postscript_prop = bpy.data.texts[post_script_name]
            if bpy.context.scene.campanprops.playblast_postscript_checkbox_prop:
                exec(bpy.context.scene.campanprops.playblast_postscript_prop.as_string())
'''

# get addon name and version to use them automaticaly in the addon
Addon_Name = str(bl_info["name"])
Addon_Version = str(bl_info["version"])
Addon_Version = Addon_Version[1:-1].replace(",",".")

import os
import bpy

# Define global variables
debug_mode = False
separator = "-" * 20
snap_folder = "Snap_Files"

## define addon preferences
class SOP_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        pass

# Create property group
class RENDER_setoutputpathprop(bpy.types.PropertyGroup):
    scenes_selection_options = [
        ("ALL SCENES", "ALL SCENES", "ALL SCENES"),
        ("CURRENT SCENE", "CURRENT SCENE", "CURRENT SCENE"),
        ("ALL SCENES WITH CURRENT SETTINGS", "ALL SCENES WITH CURRENT SETTINGS", "ALL SCENES WITH CURRENT SETTINGS")
    ]
    scenes_selection: bpy.props.EnumProperty(
        items=scenes_selection_options,
        name="Change outputs",
        description="Choose selection type",
        default="CURRENT SCENE"
    )

    additional_fields = bpy.props.BoolProperty(name="",default=False,description="show more fields and options")

    output_customfield_a: bpy.props.StringProperty(default="", name="", description='First user custom field (A)')
    output_customfield_b: bpy.props.StringProperty(default="", name="", description='Second user custom field (B)')
    output_customfield_c: bpy.props.StringProperty(default="", name="", description='Third user custom field (C)')
    output_customfield_d: bpy.props.StringProperty(default="", name="", description='Fourth user custom field (D)')

    output_postscript : bpy.props.PointerProperty (type=bpy.types.Text, name="", description="Third user custom field (From Script)")
    output_postscript_checkbox : bpy.props.BoolProperty (name="", default=False, description='if on, will launch a script after changing the render path')

    output_custom_filepath: bpy.props.StringProperty(default="Output", name="Output Folder", description='Output folder filepath, the root where everything starts')
    output_path_previs: bpy.props.StringProperty(default="[Output Folder]**/", name="Path previs", description='')
    output_corresponding : bpy.props.StringProperty(name="Translation",default="",description='translate field a to field b, separated by ",". I.E. "Image=rgba,Alpha=alpha" makes Images_Alpha becomes rgba_alpha')

    filepath_options = [("Absolute", "Absolute", "Absolute"), ("Relative", "Relative", "Relative")]
    filepath_selection: bpy.props.EnumProperty(
        items=filepath_options,
        name="",
        description="Default file path format",
        default="Relative"
    )

# Create panel for output path
class RENDER_PT_setoutputpath(bpy.types.Panel):
    bl_label = f"Set Output Path - {Addon_Version}"
    bl_idname = "RENDER_PT_setoutputpath"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'

    def draw_header(self, context):
        self.layout.label(text="", icon='FILE_FOLDER')

    def draw(self, context):
        layout = self.layout
        setoutputpath_props = context.scene.setoutputpath_props
        output_pathprevis = setoutputpath_props.output_path_previs.replace("**", "")

        box = layout.box()
        row = box.row()
        split = row.split(align=True, factor=0.85)
        split.operator('render.setoutputpath', text="Set Output Path", icon="FILE_FOLDER")
        split.prop(setoutputpath_props, "filepath_selection")
        
        box = layout.box()
        row = box.row()
        split = row.split(align=True, factor=0.9)
        split.label(icon="FOLDER_REDIRECT",text=f"Path: {output_pathprevis}")
        split.operator('sop.dellastcharacter', text="", icon="TRIA_LEFT_BAR")

        # main options
        row = box.row()
        # col2 = row.column()
        def ui_blocs(list):
            iter = 0
            for char,label,descr,icon, in list:
                operator = row.operator('sop.add_character_enum', text=label,icon=icon)
                operator.character = char
                operator.tooltip = descr
                iter += 1
        # create buttons
        char_options_A = [
            ("[File Name]","", "insert File Name","FILE_BLEND"),
            ("[Scene Name]","", "insert Scene Name","SCENE_DATA"),
            ("[File Version]","", "insert File Version (need addon called snapshot files)","LINENUMBERS_ON"),
            ("[User]","","insert user's name","USER"),
            
            ("[Camera Name]","", "insert Camera Name","CAMERA_DATA"),
            ("[Layer Name]","", "insert Layer Name","RENDERLAYERS"),
            
            ("[Output Folder]","", "insert Output Folder","FILE_FOLDER"), 
        ]
        ui_blocs(char_options_A)

        row.label(text="")

        # separators
        char_options_B = [
            
            ("/", "/","insert slash", "NONE"),
            ("_", "_","insert underscore","NONE"),
            ("-", "-","insert dash","NONE"),
            (".", ".","insert dot","NONE"),
            #("\\", "\\","insert backslash", "NONE"),
        ]
        ui_blocs(char_options_B)

# Create panel for field options
class RENDER_PT_setoutputpathfieldsoptions(bpy.types.Panel):
    bl_label = "Advanced Options"
    bl_idname = "RENDER_PT_setoutputpathfieldsoptions"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = 'output'
    bl_parent_id = "RENDER_PT_setoutputpath"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='OPTIONS')

    def draw(self, context):
        setoutputpath_props = context.scene.setoutputpath_props

        layout = self.layout
        
        ### custom fields
        box = layout.box()
        row = box.row()
        row.label(text="Add custom fields:")
        row = box.row()
        split = row.split(factor=2/5)
        split.operator('sop.add_character_enum', text="Custom A").character = "[Custom A]"
        split.prop(setoutputpath_props, "output_customfield_a",text="" )
        split = row.split(factor=2/5)
        split.operator('sop.add_character_enum', text="Custom B").character = "[Custom B]"
        split.prop(setoutputpath_props, "output_customfield_b",text="" )
        row = box.row()
        split = row.split(factor=2/5)
        split.operator('sop.add_character_enum', text="Custom C").character = "[Custom C]"
        split.prop(setoutputpath_props, "output_customfield_c",text="" )
        split = row.split(factor=2/5)
        split.operator('sop.add_character_enum', text="Custom D").character = "[Custom D]"
        split.prop(setoutputpath_props, "output_customfield_d",text="" )

        ### options
        box = layout.box()
        row = box.row()

        col2 = row.column()
        col2.prop(setoutputpath_props, "output_custom_filepath",icon="FILE_FOLDER")
        row = col2.row()
        row.prop(setoutputpath_props, "output_corresponding")

        box = layout.box()
        row = box.row()
        box.active = setoutputpath_props.output_postscript_checkbox
        row.prop(setoutputpath_props, "output_postscript_checkbox", icon='SYSTEM')
        row.prop(setoutputpath_props, "output_postscript", text="Post-Script")


# Operator for deleting the last character
class SOP_OT_dellastcharacter(bpy.types.Operator):
    bl_idname = 'sop.dellastcharacter'
    bl_label = "Delete Last Character"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        output_path_previs = context.scene.setoutputpath_props.output_path_previs
        output_split = output_path_previs.split("**")
        context.scene.setoutputpath_props.output_path_previs = "**".join(output_split[:-1])
        return {"FINISHED"}

# Generic operator for adding characters
class SOP_OT_add_character_enum(bpy.types.Operator):
    bl_idname = 'sop.add_character_enum'
    bl_label = "Add Character"
    #bl_description = "Adds a character or field to the path"
    bl_options = {"REGISTER", "UNDO"}

    character: bpy.props.StringProperty()
    tooltip: bpy.props.StringProperty()

    ### add a class to add tooltip
    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        context.scene.setoutputpath_props.output_path_previs += f"**{self.character}"
        return {"FINISHED"}

# Operator for setting output path
class RENDER_OT_setoutputpath(bpy.types.Operator):
    bl_idname = 'render.setoutputpath'
    bl_label = "Set Output Path"
    bl_description = "Set the render output path based on current settings"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print(f"\n {separator} Begin Set Output Path {separator} \n")
        scenes_to_change = []
        scene_ref = context.scene
        if scene_ref.setoutputpath_props.scenes_selection in ["ALL SCENES", "ALL SCENES WITH CURRENT SETTINGS"]:
            scenes_to_change = bpy.data.scenes
        else:
            scenes_to_change = [scene_ref]

        for scene in scenes_to_change:
            if scene_ref.setoutputpath_props.scenes_selection == "ALL SCENES WITH CURRENT SETTINGS":
                scene.setoutputpath_props.output_path_previs = scene_ref.setoutputpath_props.output_path_previs
                scene.setoutputpath_props.output_custom_filepath = scene_ref.setoutputpath_props.output_custom_filepath
                scene.setoutputpath_props.output_customfield_a = scene_ref.setoutputpath_props.output_customfield_a
                scene.setoutputpath_props.output_customfield_b = scene_ref.setoutputpath_props.output_customfield_b
                scene.setoutputpath_props.scenes_selection = scene_ref.setoutputpath_props.scenes_selection
            output_path = scene.setoutputpath_props.output_path_previs
            output_split = output_path.split("**")
            print(output_split)
            ## check if relative or absolute
            if scene.setoutputpath_props.filepath_selection == "Relative":
                complete_filepath = "//"
            else:
                complete_filepath = os.path.dirname(bpy.data.filepath)

            ## add elements 
            for elem in output_split:
                if elem == "[Output Folder]":
                    elem = f"{scene.setoutputpath_props.output_custom_filepath}"
                elif elem == "[File Name]":
                    elem = os.path.basename(bpy.data.filepath).split(".")[0]
                elif elem == "[Scene Name]":
                    elem = scene.name
                elif elem == "[Camera Name]":
                    elem = scene.camera.name if scene.camera else ""
                elif elem == "[Layer Name]":
                    elem = bpy.context.view_layer.name
                elif elem == "[User]":
                    elem = os.getlogin()
                elif elem == "[Custom A]":
                    elem = scene.setoutputpath_props.output_customfield_a
                elif elem == "[Custom B]":
                    elem = scene.setoutputpath_props.output_customfield_b
                elif elem == "[Custom C]":
                    elem = scene.setoutputpath_props.output_customfield_c
                elif elem == "[Custom D]":
                    elem = scene.setoutputpath_props.output_customfield_d
                elif elem == "[File Version]":
                    if hasattr(bpy.context.scene, "sop_props"):
                        file_version = getattr(bpy.context.scene.sop_props, "file_version")
                    elif 'Snapshots_History' in bpy.data.texts.keys(): # if older version of snapshot file
                        snap_history = bpy.data.texts['Snapshots_History'].lines[0].body
                        file_version = snap_history.replace("--", "").split(":")[-1].strip()
                    else:
                        file_version = "v001"
                    elem = file_version

                # allow user to use bpy. blablabla
                if elem.startswith("bpy."):
                    parts = elem.split(".")
                    obj = bpy
                    for part in parts[1:]:  # ignore "bpy"
                        obj = getattr(obj, part)
                    elem = obj

                complete_filepath += elem
            # clean the filepath
            clean_filepath = complete_filepath.replace("\\\\", "\\").replace("\\//", "//").replace("////", "//")
            print(f"{clean_filepath=}")
            # translate filepath regarding what user needs
            if scene.setoutputpath_props.output_corresponding != "":
                corresponding_list = scene.setoutputpath_props.output_corresponding.split(',')
                corresponding_dict = {}
                for corres in corresponding_list:
                    corres = corres.replace(" ","")
                    corres_split = corres.split("=")
                    corresponding_dict[corres_split[0]] = corres_split[-1]
                print(f"{corresponding_dict=}")
                # check if user wants to change the string
                for string in corresponding_dict.keys():
                    if string in clean_filepath :
                        clean_filepath = clean_filepath.replace(string,corresponding_dict.get(string))
            
            # change filepath
            scene.render.filepath = clean_filepath

            # use a user script if wanted
            if scene.setoutputpath_props.output_postscript_checkbox:
                if scene.setoutputpath_props.output_postscript != None: 
                    exec(scene.setoutputpath_props.output_postscript.as_string())
                    print(f"script {scene.setoutputpath_props.output_postscript.name} launched")

        print(f"\n {separator} Set Output Path Finished {separator} \n")
        return {"FINISHED"}

# Register classes
classes = (
    SOP_preferences,
    RENDER_setoutputpathprop,
    RENDER_PT_setoutputpath,
    RENDER_PT_setoutputpathfieldsoptions,
    SOP_OT_dellastcharacter,
    SOP_OT_add_character_enum,
    RENDER_OT_setoutputpath,
)

sopaddon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.setoutputpath_props = bpy.props.PointerProperty(type=RENDER_setoutputpathprop)

def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.setoutputpath_props

if __name__ == "__main__":
    register()
