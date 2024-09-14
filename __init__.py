bl_info = {
    "name": "GridArray",
    "author": "KSYN",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Modifiers",
    "description": "Create grid-like arrays along X, Y, and Z axes",
    "category": "Object",
}
import bpy

# プロパティクラスの定義
class ArrayModifierProperties(bpy.types.PropertyGroup):
    count_x: bpy.props.IntProperty(name="Count X", default=1, min=1, update=lambda self, ctx: update_modifier(self, ctx, axis='X')) # type: ignore
    count_y: bpy.props.IntProperty(name="Count Y", default=1, min=1, update=lambda self, ctx: update_modifier(self, ctx, axis='Y')) # type: ignore
    count_z: bpy.props.IntProperty(name="Count Z", default=1, min=1, update=lambda self, ctx: update_modifier(self, ctx, axis='Z')) # type: ignore
    
    offset_x: bpy.props.FloatVectorProperty(name="Offset X", size=3, default=(1.0, 0.0, 0.0), update=lambda self, ctx: update_modifier(self, ctx, axis='X')) # type: ignore
    offset_y: bpy.props.FloatVectorProperty(name="Offset Y", size=3, default=(0.0, 1.0, 0.0), update=lambda self, ctx: update_modifier(self, ctx, axis='Y')) # type: ignore
    offset_z: bpy.props.FloatVectorProperty(name="Offset Z", size=3, default=(0.0, 0.0, 1.0), update=lambda self, ctx: update_modifier(self, ctx, axis='Z')) # type: ignore
    
    distance_x: bpy.props.FloatVectorProperty(name="Distance X", size=3, default=(0.0, 0.0, 0.0), update=lambda self, ctx: update_modifier(self, ctx, axis='X')) # type: ignore
    distance_y: bpy.props.FloatVectorProperty(name="Distance Y", size=3, default=(0.0, 0.0, 0.0), update=lambda self, ctx: update_modifier(self, ctx, axis='Y')) # type: ignore
    distance_z: bpy.props.FloatVectorProperty(name="Distance Z", size=3, default=(0.0, 0.0, 0.0), update=lambda self, ctx: update_modifier(self, ctx, axis='Z')) # type: ignore
    
    merge_x: bpy.props.BoolProperty(name="Merge X", default=False, update=lambda self, ctx: update_modifier(self, ctx, axis='X')) # type: ignore
    merge_y: bpy.props.BoolProperty(name="Merge Y", default=False, update=lambda self, ctx: update_modifier(self, ctx, axis='Y')) # type: ignore
    merge_z: bpy.props.BoolProperty(name="Merge Z", default=False, update=lambda self, ctx: update_modifier(self, ctx, axis='Z')) # type: ignore

# モディファイアー更新関数
def update_modifier(self, context, axis):
    obj = context.object
    if obj:
        mod_name = f"ksynArray_{axis}"
        mod = obj.modifiers.get(mod_name)
        
        if mod:
            count = getattr(obj.array_modifier_properties, f"count_{axis.lower()}")
            offset = getattr(obj.array_modifier_properties, f"offset_{axis.lower()}")
            distance = getattr(obj.array_modifier_properties, f"distance_{axis.lower()}")
            merge = getattr(obj.array_modifier_properties, f"merge_{axis.lower()}")
            
            mod.count = count
            mod.use_merge_vertices = merge
            mod.merge_threshold = 0.01
            mod.use_relative_offset = True
            mod.relative_offset_displace = offset
            mod.use_constant_offset = True
            mod.constant_offset_displace = distance
        else:
            mod = obj.modifiers.new(mod_name, 'ARRAY')
            mod.count = getattr(obj.array_modifier_properties, f"count_{axis.lower()}")
            mod.use_merge_vertices = getattr(obj.array_modifier_properties, f"merge_{axis.lower()}")
            mod.use_relative_offset = True
            mod.relative_offset_displace = getattr(obj.array_modifier_properties, f"offset_{axis.lower()}")
            mod.use_constant_offset = True
            mod.constant_offset_displace = getattr(obj.array_modifier_properties, f"distance_{axis.lower()}")

# オペレーター: モディファイアーをX, Y, Z軸分追加
class OT_AddArrayModifiers(bpy.types.Operator):
    bl_idname = "object.add_array_modifiers"
    bl_label = "Add Array Modifiers"
    
    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        
        for axis in ['X', 'Y', 'Z']:
            mod_name = f"Array_{axis}"
            if not obj.modifiers.get(mod_name):
                mod = obj.modifiers.new(mod_name, 'ARRAY')
                mod.use_relative_offset = True
                mod.relative_offset_displace = (0.0, 0.0, 0.0)
                mod.use_constant_offset = True
                mod.constant_offset_displace = (0.0, 0.0, 0.0)
                mod.count = 1
        return {'FINISHED'}

# パネルの作成 (3Dビュー用)
class VIEW3D_PT_ArrayModifierPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_array_modifier_panel"
    bl_label = "Array Modifier Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Modifiers"
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj:
            layout.operator("object.add_array_modifiers", text="Add Array Modifiers")
            
            props = obj.array_modifier_properties
            
            row=layout.row()
            for axis in ['x', 'y', 'z']:
                box = row.box()
                box.label(text=f"Array {axis.upper()}")
                box.prop(props, f"count_{axis}")
                
                offset_prop = box.column(align=True)
                offset_prop.prop(props, f"offset_{axis}", text="Offset")
                
                distance_prop = box.column(align=True)
                distance_prop.prop(props, f"distance_{axis}", text="Distance")
                
                box.prop(props, f"merge_{axis}")

# クラス登録・解除関数
classes = [
    ArrayModifierProperties,
    OT_AddArrayModifiers,
    VIEW3D_PT_ArrayModifierPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.array_modifier_properties = bpy.props.PointerProperty(type=ArrayModifierProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.array_modifier_properties

if __name__ == "__main__":
    register()