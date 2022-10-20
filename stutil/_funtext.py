
import stutil

__text_length = 62


ASCII_LOGO = r'''
         ______   ______  __  __   ______  __   __
        /\  ___\ /\__  _\/\ \/\ \ /\__  _\/\ \ /\ \
 )\_/(  \ \___  \\/_/\ \/\ \ \_\ \\/_/\ \/\ \ \\ \ \____
='o.o'=  \/\_____\  \ \_\ \ \_____\  \ \_\ \ \_\\ \_____\
 (_ _)    \/_____/   \/_/  \/_____/   \/_/  \/_/ \/_____/
    U                    version: {version}
'''.format(version=stutil.__version__)

DESCRIPTION = 'UTILities for STomoya (stutil)'

HEADER = f'{ASCII_LOGO}\n{DESCRIPTION.center(__text_length)}'

def get_detailed_header():
    urls = 'GitHub: https://github.com/STomoya/stutil'.center(__text_length)

    detailed_header = '\n\n'.join([HEADER, urls])

    return detailed_header
