import fileinput
import glob

file_list = glob.glob("all_files.html")

with open('result.html', 'w') as file:
    input_lines = fileinput.input(file_list)
    file.writelines(input_lines)
