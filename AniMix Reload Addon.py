# Information about the addon
bl_info = {
    "name": "AniMix Reload Addon",
    "author": "Adam Earle",
    "version": (1, 0),
    "blender": (2, 91, 0),
    "location": "Preferences > Add-ons",
    "description": "Refreshes the specified addons",
    "warning": "",
    "wiki_url": "",
    "category": "AniMix",
}

# Import necessary modules
import bpy
import os

# Define a UI list class for displaying addons
class ADDON_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        addon = item
        row = layout.row(align=True)
        row.separator(factor=0.5)
        row.prop(addon, "is_selected", text="")
        row.separator(factor=0.5)

        # Remove the "Name:" and "Path:" prefixes from the labels
        row.label(text=f"{addon.module}", translate=False)
        row.label(text=f"{addon.filepath}", translate=False)

        row.separator(factor=0.5)
        row.operator("addon.reload", text="", icon='FILE_REFRESH').addon_index = index

# Define an operator for reloading a specific addon
class ADDON_OT_reload(bpy.types.Operator):
    bl_idname = "addon.reload"
    bl_label = "Reload Addon"
    addon_index: bpy.props.IntProperty()  # Index of the addon to reload

    # This method is called when the operator is executed
    def execute(self, context):
        addon = context.window_manager.addon_list[self.addon_index]

        # Check if the addon is enabled before trying to disable it
        if bpy.ops.preferences.addon_disable.poll():
            try:
                bpy.ops.preferences.addon_disable(module=addon.module)
            except ValueError:
                pass

        # Check if the addon is disabled before trying to enable it
        if bpy.ops.preferences.addon_enable.poll():
            try:
                bpy.ops.preferences.addon_enable(module=addon.module)
            except ValueError:
                pass

        return {'FINISHED'}

# Define an operator for reloading all addons
class ADDON_OT_reload_all(bpy.types.Operator):
    bl_idname = "addon.reload_all"
    bl_label = "Reload All Addons"

    # This method is called when the operator is executed
    def execute(self, context):
        for addon in context.window_manager.addon_list:
            if addon.is_selected:  # Only reload the addon if it's selected
                bpy.ops.preferences.addon_disable(module=addon.module)
                bpy.ops.preferences.addon_enable(module=addon.module)
        return {'FINISHED'}



    # Execute the operator
    def execute(self, context):
        for addon in context.window_manager.addon_list:
            bpy.ops.preferences.addon_disable(module=addon.module)
            bpy.ops.preferences.addon_enable(module=addon.module)
        return {'FINISHED'}

# Define an operator for getting the list of enabled addons
class ADDON_OT_get_addon_list(bpy.types.Operator):
    bl_idname = "addon.get_addon_list"
    bl_label = "Get Enabled Addons"

    # Define a function to use as the sorting key
    def get_module(self, addon):
        return addon.module

    # Execute the operator
    def execute(self, context):
        wm = context.window_manager
        wm.addon_list.clear()

        # Get all enabled addons and sort them by module name
        sorted_addons = sorted(bpy.context.preferences.addons, key=self.get_module)

        # Loop through all enabled addons
        for addon in sorted_addons:
            # Add each addon to the list
            item = wm.addon_list.add()
            item.module = addon.module

            # Try to access the 'filepath' attribute
            try:
                item.filepath = addon.filepath
            except AttributeError:
                # If 'filepath' attribute is not available, set a default value or handle it accordingly
                item.filepath = "Filepath not available"

        return {'FINISHED'}


# Define an operator for clearing the list of addons
class ADDON_OT_clear_addon_list(bpy.types.Operator):
    bl_idname = "addon.clear_addon_list"
    bl_label = "Clear Addon List"

    # Execute the operator
    def execute(self, context):
        context.window_manager.addon_list.clear()
        return {'FINISHED'}

# Define an operator for choosing an addon
class ADDON_OT_choose_addon(bpy.types.Operator):
    bl_idname = "addon.choose_addon"
    bl_label = "Choose Addon"
    addon_index: bpy.props.IntProperty()  # Index of the addon to choose

    # Execute the operator
    def execute(self, context):
        addon = context.window_manager.addon_list[self.addon_index]
        addon.is_selected = not addon.is_selected
        return {'FINISHED'}

# Define# Define a panel for the addon
class ADDON_PT_main_panel(bpy.types.Panel):
    bl_label = "AniMix Reload Addon"
    bl_idname = "ADDON_PT_main_panel"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"

    # Draw the panel
    def draw(self, context):
        layout = self.layout    
        wm = context.window_manager

        # Add a row with the "Get Addon List", "Clear Addon List" and "Reload All Addons" buttons
        row = layout.row()
        row.operator("addon.get_addon_list")
        row.operator("addon.clear_addon_list")
        row.operator("addon.reload_all")

        # Add a list for all addons
        row = layout.row(align=True)
        row.template_list("ADDON_UL_list", "", wm, "addon_list", wm, "addon_list_index", item_dyntip_propname="module", rows=1, maxrows=5)

# Define a property group for the addons
class AddonItem(bpy.types.PropertyGroup):
    module: bpy.props.StringProperty()  # Module name of the addon
    filepath: bpy.props.StringProperty()  # Filepath of the addon
    is_selected: bpy.props.BoolProperty(default=False)  # Whether the addon is selected

# List of all classes to register
classes = [ADDON_UL_list, ADDON_OT_reload, ADDON_OT_reload_all, ADDON_OT_get_addon_list, ADDON_OT_clear_addon_list, ADDON_OT_choose_addon, ADDON_PT_main_panel, AddonItem]

# Register all classes and properties
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.addon_list = bpy.props.CollectionProperty(type=AddonItem)
    bpy.types.WindowManager.addon_list_index = bpy.props.IntProperty()

# Unregister all classes and properties
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.addon_list
    del bpy.types.WindowManager.addon_list_index

# Run the register function when the script is run
if __name__ == "__main__":
    register()
