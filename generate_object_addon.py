import bpy

bl_info = {
    "name": "Генерация 3D-объекта",
    "author": "NaLLsuR",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tool",
    "description": "Добавляет вкладку для генерации 3D-объекта по промпту",
    "category": "Object",
}

# Свойство для хранения текста промпта
class PromptProperty(bpy.types.PropertyGroup):
    user_prompt: bpy.props.StringProperty(
        name="Промпт",
        description="Введите текст для генерации",
        default="",
        maxlen=1024,
    )

# Оператор для обработки кнопки
class OBJECT_OT_generate_from_prompt(bpy.types.Operator):
    bl_idname = "object.generate_from_prompt"
    bl_label = "Сгенерировать"
    bl_description = "Сгенерировать объект на основе введенного промпта"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prompt = context.scene.prompt_properties.user_prompt
        if not prompt:
            self.report({'ERROR'}, "Пожалуйста, введите текст для генерации")
            return {'CANCELLED'}
        
        # Пока что просто создадим куб и напечатаем промпт
        bpy.ops.mesh.primitive_cube_add(size=2)
        self.report({'INFO'}, f"Сгенерировано на основе промпта: {prompt}")
        return {'FINISHED'}

# Панель для интерфейса
class VIEW3D_PT_generate_panel(bpy.types.Panel):
    bl_label = "Генерация 3D-объекта"
    bl_idname = "VIEW3D_PT_generate_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Generate'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Поле для ввода текста
        layout.prop(scene.prompt_properties, "user_prompt")

        # Кнопка для генерации
        layout.operator(OBJECT_OT_generate_from_prompt.bl_idname)

# Регистрация классов
classes = [
    PromptProperty,
    OBJECT_OT_generate_from_prompt,
    VIEW3D_PT_generate_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prompt_properties = bpy.props.PointerProperty(type=PromptProperty)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.prompt_properties

if __name__ == "__main__":
    register()
