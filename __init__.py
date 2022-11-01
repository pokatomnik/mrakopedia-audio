import json
from convert import convert_textfile_to_audio

with open("data/index.json", "r", encoding="utf-8") as file:
    json_str = file.read()
index_json = json.loads(json_str)
index = index_json["mrakopediaIndex"]

dict = {}

cateogory_names = index.keys()

for category_name in cateogory_names:
    category = index[category_name]
    for page_meta in category:
        page_title = page_meta["title"]
        dict[page_title] = page_meta

with open("out/index.json", "w", encoding="utf-8") as file:
    serialized_json = json.dumps(dict)
    file.write(serialized_json)

for category_title, page_meta in dict.items():
    content_id = page_meta["contentId"]
    input_file_name = content_id + ".md"
    output_file_name = content_id + ".mp3"

    input_file_path = "data/" + input_file_name
    output_file_path = "out/" + output_file_name

    print(page_title)
    print(input_file_path)
    
    convert_textfile_to_audio(input_file_path, output_file_path)
