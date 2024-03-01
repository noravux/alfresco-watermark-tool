import os
import time
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from watermarker import apply_watermark
from dotenv import load_dotenv

load_dotenv()

input_dir = os.getenv('INPUT_DIR', 'input')
output_dir = os.getenv('OUTPUT_DIR', 'output')
watermark_pdf = os.getenv('WATERMARK_PDF')
position = os.getenv('POSITION')
scale = float(os.getenv('SCALE', 1.0))
alfresco_url = os.getenv('ALFRESCO_URL')
cookie = os.getenv('COOKIE')
node_id = os.getenv('NODE_ID')

# Check if input_dir exists, create it if not
if not os.path.exists(input_dir):
    os.makedirs(input_dir)

# Check if output_dir exists, create it if not
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def create_form(file_path, title=None, description=None):
    file_data = open(file_path, 'rb')

    form_data = {
        'nodeType': (None, 'cm:content'),
        'filedata': (os.path.basename(file_path), file_data),
    }

    if title:
        form_data['cm:title'] = (None, title)
    if description:
        form_data['cm:description'] = (None, description)

    return form_data

def process_file(item, s, base_url, node_id):
    try:
        if item['entry']['name'].endswith('.pdf'):
            # Download the file
            response = s.get(f"{base_url}/nodes/{item['entry']['id']}/content")
            file_info = s.get(f"{base_url}/nodes/{item['entry']['id']}").json()
            with open(f'input/{item["entry"]["name"]}', 'wb') as f:
                f.write(response.content)
            # Add watermark
            input_pdf_path = f'{input_dir}/{item["entry"]["name"]}'
            output_pdf_path = f'{output_dir}/{item["entry"]["name"].replace(".pdf", "_watermarked.pdf")}'
            apply_watermark(input_pdf_path, watermark_pdf, output_pdf_path, position, scale)

            properties = file_info['entry'].get('properties', {})

            title = properties.get('cm:title', None)
            description = properties.get('cm:description', None)

            # Upload the file back to Alfresco
            form_data = create_form(output_pdf_path, title=title, description=description)
            response = s.post(f"{base_url}/nodes/{node_id}/children", files=form_data)
    except Exception as e:
        print(f"An error occurred while processing file {item['entry']['name']}: {e}")


def process_files(node_id, s=None):
    if s is None:
        s = requests.Session()
        s.headers.update({
        "cookie": cookie
        })
    base_url = alfresco_url

    try:
        response = s.get(f"{base_url}/nodes/{node_id}/children")       
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e) 
    else:
        data = response.json()
        print(f"Processing {len(data['list']['entries'])} files...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for item in data['list']['entries']:
                if item['entry']['isFolder']:
                    # If the item is a folder, process its files recursively
                    process_files(item['entry']['id'], s)
                else:
                    # If the item is a file, process it
                    futures.append(executor.submit(process_file, item, s, base_url, node_id))
        print(f"{len(futures)} files to watermark.")
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")
                    
start_time = time.time()

process_files(node_id)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Took {elapsed_time} seconds to complete.")