import argparse


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


def play_from_nuc_generator(gen):
    while True:
        chord = [next(gen) for _ in range(3)]

        print(next(gen))


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
        play_from_nuc_generator(nuc_generator)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

