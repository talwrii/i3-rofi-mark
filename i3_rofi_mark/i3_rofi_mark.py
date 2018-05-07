
import json
import logging
import argparse
import subprocess

LOGGER = logging.getLogger()

def rofi_prompt(prompt, choices):
    p = subprocess.Popen(
        ['rofi', '-dmenu', '-p', prompt],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    choice_string = '\n'.join(choices)
    reply, _ = p.communicate(choice_string.encode('utf8'))
    return reply.strip().decode('utf8')


def get_marks():
    marks = json.loads(subprocess.check_output(["i3-msg", "-t", 'get_marks'], stderr=subprocess.PIPE))
    return marks

def mark_window(mark):
    subprocess.check_call(
        ["i3-msg", "-t", "command", "mark {}".format(mark)],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)


def select_window(mark):
    command = ['i3-msg', '-t', 'command', '[con_mark="{}"] focus'.format(mark)]
    LOGGER.debug('Running: %r', command)
    subprocess.check_call(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def unmark(mark):
    subprocess.check_call(
        ["i3-msg", "-t", "command", "unmark {}".format(mark)],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)

def build_parser():
    parser = argparse.ArgumentParser(description='', prog='i3-rofi-mark')
    parser.add_argument('--debug', action='store_true', help='Include debug output (to stderr)')
    parser.add_argument('--prefix', type=str, help='Show or add this prefix')
    parsers = parser.add_subparsers(dest='command')
    parsers.required = True
    mark_parser = parsers.add_parser('mark')
    goto_parser = parsers.add_parser('goto')
    goto_parser = parsers.add_parser('unmark')
    return parser

def zenity_read(prompt):
    return subprocess.check_output(['zenity', '--entry'] + (['--text', prompt] if prompt else [])).decode('utf8')

def main():
    args = build_parser().parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.command == 'goto':
        marks = get_marks()

        if args.prefix is not None:
            marks = [mark[args.prefix:] for mark in get_marks() if mark.startswith(args.prefix)]

        LOGGER.debug('marks: %r', marks)
        window = rofi_prompt("Window", marks)
        if args.prefix is not None:
            window = args.prefix + window
        LOGGER.debug('Selecting window %r', window)
        select_window(window)
    elif args.command == 'mark':
        mark = zenity_read("Mark")
        if args.prefix is not None:
            mark = args.prefix + mark
        LOGGER.debug('Marking with %r', mark)
        mark_window(mark)
    elif args.command == 'unmark':
        marks = get_marks()

        if args.prefix is not None:
            marks = [mark[len(args.prefix):] for mark in get_marks() if mark.startswith(args.prefix)]

        mark = rofi_prompt("Get marks", marks)
        if args.prefix:
            mark = args.prefix + mark
        unmark(mark)
    else:
        raise ValueError(args.command)
