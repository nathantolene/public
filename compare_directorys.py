import os


def main():
    shared_screen_path = input('Path to shared_screen')
    active_speaker_path = input('Path to active speaker')
    print(shared_screen_path)
    print(active_speaker_path)
    shared_screen_files = os.listdir(shared_screen_path)
    active_speaker_files = os.listdir(active_speaker_path)
    print(shared_screen_files)
    print(active_speaker_files)
    needs_moved = list(set(active_speaker_files) - set(shared_screen_files))
    for x in needs_moved:
        print(x)
        print(active_speaker_path, x)
        print(shared_screen_path, x)
        os.system(f'sudo cp {active_speaker_path}{x} {shared_screen_path}')
        break


if __name__ == '__main__':
    main()
