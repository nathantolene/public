import os
import shutil


path1 = '/smb/Zoom/downloads/shared_screen_with_speaker_view/ACCT 305 Hatch'
path2 = '/smb/Zoom/downloads/active_speaker/ACCT 305 Hatch'

def main():
    # shared_screen_path = input('Path to shared_screen')
    shared_screen_path = path1
    # active_speaker_path = input('Path to active speaker')
    active_speaker_path = path2
    # print(shared_screen_path)
    # print(active_speaker_path)
    shared_screen_files = os.listdir(shared_screen_path)
    active_speaker_files = os.listdir(active_speaker_path)
    # print(shared_screen_files)
    # print(active_speaker_files)
    needs_moved = list(set(active_speaker_files) - set(shared_screen_files))
    for x in needs_moved:
        print(x)
        # active_speaker_path = active_speaker_path.replace(" ", "\\ ")
        active_speaker_path = f'{active_speaker_path}/{x}'
        # shared_screen_path = shared_screen_path.replace(" ", "\ ")
        shared_screen_path = f'{shared_screen_path}/{x}'
        print(f'{active_speaker_path}')
        print(f'{shared_screen_path}')
        # print(f'cp "{active_speaker_path}" "{shared_screen_path}/"')
        # os.system(f'cp "{active_speaker_path}/{x}" "{shared_screen_path}/"')
        # os.system(f'cp {active_speaker_path}/{x} {shared_screen_path}')
        shutil.copyfile(f'{active_speaker_path}', f'{shared_screen_path}')
        # break


if __name__ == '__main__':
    main()
