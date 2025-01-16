import bpy
import requests
import tempfile
import os

bl_info = {
    "name": "Генерация 3D-объекта",
    "author": "NaLLsuR",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tool",
    "description": "Добавляет вкладку для генерации 3D-объекта по промпту",
    "category": "Object",
}

class PLYGeneratorPanel(bpy.types.Panel):
    """Панель для генерации 3D объектов"""
    bl_label = "Генератор PLY"
    bl_idname = "VIEW3D_PT_ply_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Генерация'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene, "prompt_text")
        layout.operator("object.generate_ply", text="Сгенерировать")

class GeneratePLYOperator(bpy.types.Operator):
    """Генерация PLY через API"""
    bl_idname = "object.generate_ply"
    bl_label = "Сгенерировать PLY"
    
    def execute(self, context):
        scene = context.scene
        prompt = scene.prompt_text
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_dir, exist_ok=True) 

        # URL вашего API
        api_url = "https://979e-34-91-212-248.ngrok-free.app/generate"
        payload = {"prompt": prompt}
        
        try:
            # Отправка запроса на API
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            
            # Сохранение полученного файла
            filepath = os.path.join(downloads_dir, f"{prompt}.ply")
            with open(filepath, 'wb') as file:
                file.write(response.content)
            
            #with tempfile.NamedTemporaryFile(delete=False, suffix=".ply") as temp_file:
            #    temp_file.write(response.content)
            #    temp_filepath = temp_file.name
            #self.report(f"Temporary PLY file saved at: {temp_filepath}")
            
            # Импорт файла в Blender
            bpy.ops.wm.ply_import(filepath=filepath )
            
            # Удаление временного файла
            #os.remove(temp_filepath)
            
            self.report({'INFO'}, "PLY успешно сгенерирован и загружен")
        except requests.RequestException as e:
            self.report({'ERROR'}, f"Ошибка API: {e}")
        except Exception as e:
            self.report({'ERROR'}, f"Ошибка загрузки PLY: {e}")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PLYGeneratorPanel)
    bpy.utils.register_class(GeneratePLYOperator)
    bpy.types.Scene.prompt_text = bpy.props.StringProperty(
        name="Текстовый запрос",
        description="Введите текстовый запрос для генерации 3D объекта",
        default=""
    )

def unregister():
    bpy.utils.unregister_class(PLYGeneratorPanel)
    bpy.utils.unregister_class(GeneratePLYOperator)
    del bpy.types.Scene.prompt_text

if __name__ == "__main__":
    register()