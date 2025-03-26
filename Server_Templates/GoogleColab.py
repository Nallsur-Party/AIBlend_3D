! pip install plotly -q
! git clone https://github.com/openai/point-e #клонируем репозиторий
%cd point-e
#переходим внутрь папки
! pip install -e . #устанавливаем подготовленные библиотеки


import torch
from tqdm.auto import tqdm

from point_e.diffusion.configs import DIFFUSION_CONFIGS, diffusion_from_config
from point_e.diffusion.sampler import PointCloudSampler
from point_e.models.download import load_checkpoint
from point_e.models.configs import MODEL_CONFIGS, model_from_config
from point_e.util.plotting import plot_point_cloud

# Проверка доступности GPU для ускорения обработки
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Создание базовой модели Point-E и модели для увеличения размерности
print('creating base model...')
base_name = 'base40M-textvec'
base_model = model_from_config(MODEL_CONFIGS[base_name], device)
base_model.eval()
base_diffusion = diffusion_from_config(DIFFUSION_CONFIGS[base_name])

print('creating upsample model...')
upsample_name = 'upsample'
upsampler_model = model_from_config(MODEL_CONFIGS[upsample_name], device)
upsampler_model.eval()
upsampler_diffusion = diffusion_from_config(DIFFUSION_CONFIGS[upsample_name])

# Загрузка предварительно обученных весов для базовой и увеличенной моделей
print('downloading base checkpoint...')
base_model.load_state_dict(load_checkpoint(base_name, device))

print('downloading upsampler checkpoint...')
upsampler_model.load_state_dict(load_checkpoint(upsample_name, device))

# Создание объекта для генерации облака точек
sampler = PointCloudSampler(
    device=device,
    models=[base_model, upsampler_model],
    diffusions=[base_diffusion, upsampler_diffusion],
    num_points=[1024, 4096 - 1024],
    aux_channels=['R', 'G', 'B'],
    guidance_scale=[3.0, 0.0],
    model_kwargs_key_filter=('texts', ''), # оптимальные параметры
)

#Часть с API
!pip install flask flask-cors pyngrok
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pyngrok import ngrok
import os
from io import BytesIO

import skimage.measure as measure
from point_e.util.pc_to_mesh import marching_cubes_mesh

app = Flask(__name__)
CORS(app)

# Экспорт в файл .ply для импорта в другие программы, например Blender
@app.route('/generate', methods=['POST'])
def generate():
  data = request.json
  prompt = data.get('prompt', 'default')


  # Код ниже строит образец для создания облака точек
  samples = None
  for x in tqdm(sampler.sample_batch_progressive(batch_size=1, model_kwargs=dict(texts=[prompt]))):
      samples = x
  pc = sampler.output_to_point_clouds(samples)[0]

  #sdf model
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  print('creating SDF model...')
  name = 'sdf'
  model = model_from_config(MODEL_CONFIGS[name], device)
  model.eval()
  print('loading SDF model...')
  model.load_state_dict(load_checkpoint(name, device))

  #создание меша
  mesh = marching_cubes_mesh(
      pc=pc,
      model=model,
      batch_size=4096,

      grid_size=32, # 'настраиваемые параметры сетки'
      progress=True,
  )

  # Записываем .ply файл в память
  ply_output = BytesIO()
  mesh.write_ply(ply_output)
  ply_output.seek(0) # Устанавливаем указатель на начало

  ##filename = f'{prompt}.ply'
  ##with open(filename , 'wb') as mesh_file:
  ##    mesh.write_ply(mesh_file)
  ##return jsonify({"status": "success", "file": filename})

  # Отправляем файл клиенту
  return send_file(ply_output, as_attachment=True, download_name=f"{prompt}.ply", mimetype='application/octet-stream')

from google.colab import drive
drive.mount('/content/drive')

# Чтение файла для токкена ngrock (вставьте сюда свой токкен)
with open('/content/drive/My Drive/ControlPassword/token_ngrock.txt', 'r') as file:
    secret = file.read()
print(secret)
!ngrok authtoken {secret}
public_url = ngrok.connect(5000).public_url
print(f"API доступно по адресу: {public_url}")
app.run(port=5000)