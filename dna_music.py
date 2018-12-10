import argparse
from itertools import product
import time

import pygame
import pygame.midi

CODONS = list(''.join(p) for p in product('atgc', repeat=3))

MIDI_NOTES_BY_CODON = {codon: i for i, codon in enumerate(CODONS, start=32)}

MIDI_CHORDS_BY_CODON = {codon: (i, i + 2, i + 4) for i, codon in enumerate(CODONS, start=32)}

VOLUME = 127
PERIOD = 0.33
PERIOD = 0.17
MIDDLE_C = 60


def chord_on_off(midi_out, chord_codon, note_on=True):
    chord_notes = MIDI_CHORDS_BY_CODON.get(chord_codon)
    for note in chord_notes:
        getattr(midi_out, 'note_on' if note_on else 'note_off')(note, VOLUME)


def play_bar(midi_out, chord_codon, codon1, codon2, codon3):
    note = MIDI_NOTES_BY_CODON.get(codon1, MIDDLE_C)
    midi_out.note_on(note, VOLUME)
    time.sleep(PERIOD)
    midi_out.note_off(note, VOLUME)

    note = MIDI_NOTES_BY_CODON.get(codon2, MIDDLE_C)
    midi_out.note_on(note, VOLUME)
    time.sleep(PERIOD)
    midi_out.note_off(note, VOLUME)

    note = MIDI_NOTES_BY_CODON.get(codon3, MIDDLE_C)
    midi_out.note_on(note, VOLUME)
    time.sleep(PERIOD)
    midi_out.note_off(note, VOLUME)



def generate_nucs_from_path(path, skip_heterochromatin=True):
    try:
        with open(path) as fp:
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


def play_from_nuc_generator(midi_out, gen, offset=0):
    i = 0
    while True:
        i += 1

        chord = ''.join(next(gen) for _ in range(3))
        note1 = ''.join(next(gen) for _ in range(3))
        note2 = ''.join(next(gen) for _ in range(3))
        note3 = ''.join(next(gen) for _ in range(3))

        if offset >= i:  # don't play these notes if we are below the offset
            continue

        print(time.time(), chord, note1, note2, note3)
        play_bar(midi_out, chord, note1, note2, note3)



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('-p', '--play-heterochromatin',
                        action='store_true',
                        default=False)
    parser.add_argument('-o', '--offset',
                        type=int,
                        default=0)



    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    nuc_generator = generate_nucs_from_path(
        path=args.path,
        skip_heterochromatin=not args.play_heterochromatin,
    )

    midi_out = None
    try:
        pygame.init()
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        midi_out = pygame.midi.Output(port, 0)
        midi_out.set_instrument(0)

        play_from_nuc_generator(midi_out, nuc_generator, args.offset)
    except KeyboardInterrupt:
        pass

    finally:
        del midi_out
        pygame.midi.quit()


if __name__ == '__main__':
    main()

