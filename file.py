import os
import json

def init_data_file(data_dir, data_file_name):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filename = f"{data_dir}/{data_file_name}"
    
    # Create file if it doesn't exist
    if not os.path.isfile(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    
    # Read existing data
    data = {}
    with open(filename, 'r') as f:
        content = f.read()
        data = json.loads(content) if content else {}

    return data, filename

def save_model_to_file(data, filename, model, id):
    # Ajouter le nouveau modèle
    data[id] = model
    
    # Écrire le tout
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)