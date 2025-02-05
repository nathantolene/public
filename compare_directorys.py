import os
import shutil

path1 = '/smb/Zoom/downloads/shared_screen_with_speaker_view/ACCT 305 Hatch'
path2 = '/smb/Zoom/downloads/active_speaker/ACCT 305 Hatch'


def missing():
    returner = []
    with open('missing.txt', 'r') as file:
        for line in file:
            new_line = line.split(" ")
            remove_new_line = new_line[18]
            remove_new_line = remove_new_line.replace("\n", "")
            folder_name = f'{new_line[16]} {new_line[17]} {remove_new_line}'
            returner.append(folder_name)
    return returner


def main():
    missed = missing()
    shared_screen_path_set = path1
    active_speaker_path_set = path2
    shared_screen_files = os.listdir(shared_screen_path_set)
    active_speaker_files = os.listdir(active_speaker_path_set)
    needs_moved = list(set(active_speaker_files) - set(shared_screen_files))
    for x in needs_moved:
        print(x)
        active_speaker_path = active_speaker_path_set
        active_speaker_path = f'{active_speaker_path}/{x}'
        shared_screen_path = shared_screen_path_set
        shared_screen_path = f'{shared_screen_path}/{x}'
        shutil.copyfile(f'{active_speaker_path}', f'{shared_screen_path}')


if __name__ == '__main__':
    main()
