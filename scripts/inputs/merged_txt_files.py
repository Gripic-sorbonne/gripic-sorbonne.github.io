import os

def merge_txt_files(input_folder, output_filename = "combined_all.txt"):
    
    
    file_list = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    print(f"Found {len(file_list)} text files in '{input_folder}'.")

    file_list.sort()

    with open(output_filename, "w", encoding='utf-8') as outfile:
        for file_name in file_list:

            if file_name == output_filename:
                continue

            file_path = os.path.join(input_folder, file_name)
            print(f"Merging file: {file_path} ...")

            with open(file_path, "r", encoding = 'utf-8') as infile:
                content = infile.read()
                outfile.write(content + "\n")
input_fileder = "/Users/jungmin/Desktop/gripic_sorbonne/gripic-sorbonne.github.io/scripts/inputs/input_folder"
output_file = "/Users/jungmin/Desktop/gripic_sorbonne/gripic-sorbonne.github.io/scripts/inputs/combined_all.txt"

merge_txt_files(input_fileder, output_file)

