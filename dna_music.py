import argparse
import time

import pygame
import pygame.midi


NOTES_BY_NUC = {
    'a': 72,
    'g': 78,
    't': 90,
    'c': 45,
}

CHORD_BY_NUC = {
    'a': (84, 98, 100),
    'g': (23, 54, 100),
    't': (35, 72, 100),
    'c': (90, 100, 127),
}


VOLUME = 127
PERIOD = 0.33

def chord_on(midi_out, chord):
    note1, note2, note3 = CHORD_BY_NUC.get(chord, (24, 53, 35))
    # turn on cord
    midi_out.note_on(note1, VOLUME)
    midi_out.note_on(note2, VOLUME)
    midi_out.note_on(note3, VOLUME)


def chord_off(midi_out, chord):
    note1, note2, note3 = CHORD_BY_NUC.get(chord, (24, 53, 35))
    # turn off cord
    midi_out.note_off(note1, VOLUME)
    midi_out.note_off(note2, VOLUME)
    midi_out.note_off(note3, VOLUME)


def play_bar(midi_out, chord, note1, note2, note3):
    chord_on(midi_out, chord)

    note = NOTES_BY_NUC.get(note1, 80)
    midi_out.note_on(note, VOLUME)
    time.sleep(PERIOD)
    midi_out.note_off(note, VOLUME)

    note = NOTES_BY_NUC.get(note2, 80)
    midi_out.note_on(note, VOLUME)
    time.sleep(PERIOD)
    midi_out.note_off(note, VOLUME)

    note = NOTES_BY_NUC.get(note3, 80)
    midi_out.note_on(note, VOLUME)
    time.sleep(PERIOD)
    midi_out.note_off(note, VOLUME)

    chord_off(midi_out, chord)


def generate_nucs_from_path(path, skip_heterochromatin=True):
    try:
        fp = open(path)
        for line in fp:
            line = line.strip()

            if line.startswith('>'):
                continue

            for nuc in line:
                nuc = nuc.lower().strip()
                if not nuc:
                    continue

                if skip_heterochromatin and nuc == 'n':
                    continue
                else:
                    skip_heterochromatin = False

                yield nuc

    finally:
        fp.close()


def play_from_nuc_generator(midi_out, gen):
    while True:
        nucs = ''.join(next(gen) for _ in range(4))

        print(nucs)
        play_bar(midi_out, *nucs)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('-p', '--play-heterochromatin',
                        action='store_true',
                        default=False)

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    nuc_generator = generate_nucs_from_path(
        path=args.path,
        skip_heterochromatin=not args.play_heterochromatin,
    )

    try:
        pygame.init()
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        midi_out = pygame.midi.Output(port, 0)
        midi_out.set_instrument(0)

        play_from_nuc_generator(midi_out, nuc_generator)
    except KeyboardInterrupt:
        pass

    finally:
        del midi_out
        pygame.midi.quit()


if __name__ == '__main__':
    main()

