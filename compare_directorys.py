import os
import shutil

path1 = '/smb/Zoom/downloads/shared_screen_with_speaker_view/'
path2 = '/smb/Zoom/downloads/active_speaker/'


def compare_files():
    shared_list = list_under_directory(path1)
    active_list = list_under_directory(path2)
    print(len(shared_list), len(active_list))
    # compare_lists = list(set(shared_list) - set(active_list))
    # compare_lists2 = list(set(active_list) - set(shared_list))
    # print(compare_lists)
    # print('***')
    # print(compare_lists2)


def list_under_directory(directory_path):
    returner = []
    shared_screen_list = os.scandir(directory_path)
    for x in shared_screen_list:
        if x.is_dir():
            returner.append(x.name)
    return returner


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
    shared_list = list_under_directory(path1)
    for y in shared_list:
        shared_screen_path_set = path1 + y
        active_speaker_path_set = path2 + y
        if os.path.exists(active_speaker_path_set):
            shared_screen_files = os.listdir(shared_screen_path_set)
            active_speaker_files = os.listdir(active_speaker_path_set)
            needs_moved = list(set(active_speaker_files) - set(shared_screen_files))
            needs_moved = remove_old_files(needs_moved)
            # print(needs_moved)
            for x in needs_moved:
                if 'uploaded' in x or 'SWRK' in x:
                    continue
                print(x)
                active_speaker_path = active_speaker_path_set
                active_speaker_path = f'{active_speaker_path}/{x}'
                shared_screen_path = shared_screen_path_set
                shared_screen_path = f'{shared_screen_path}/{x}'
                # shutil.copyfile(f'{active_speaker_path}', f'{shared_screen_path}')


def remove_old_files(needs_moved):
    returner = []
    for x in needs_moved:
        if '2024' not in x:
            returner.append(x)
    return returner


if __name__ == '__main__':
    main()
