import argparse

import stutil
from stutil._funtext import HEADER, get_detailed_header

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-V', action='store_true', help='Want the version?')
    parser.add_argument('--verbose', '-v', action='store_true', help='Want more detailed info?')
    args = parser.parse_args()

    if args.version:
        print('stutil version:', stutil.__version__)
    elif args.verbose:
        print(get_detailed_header())
    else:
        print(HEADER)
