#!/usr/bin/env python3
#
# Copyright (C) 2017 Olaf Lessenich
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License v2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 021110-1307, USA.

import argparse
import os
import sys

import email
import mailbox


verbose = False
oneline = False


def print_usage(path):
    print("Usage: %s [MAILDIR1] [MAILDIR2]" % path)


def is_maildir(directory):
    if not os.path.isdir(directory):
        return False

    subdirs = ['cur', 'new', 'tmp']

    for s in subdirs:
        if not os.path.isdir(os.path.join(directory, s)):
            return False

    return True


def get_maildirs(directory):
    if is_maildir(directory):
        return [directory]

    maildirs = []
    for d in os.listdir(directory):
        if is_maildir(os.path.join(directory, d)):
            maildirs.append(os.path.join(directory, d))

    return maildirs


def print_message(message_id, path, count):
    offset = (len(str(count)) + 3)

    if not oneline:
        print()
        print("%d. %s" % (count, message_id))

    if verbose:
        with open(path, 'r',
                  encoding='utf-8',
                  errors='replace') as fp:
            msg = email.message_from_file(fp)

            if oneline:
                try:
                    dt = email.utils.parsedate_to_datetime(msg['date'])
                    date = dt.strftime('%Y-%m-%d %H:%M')
                    sender = email.utils.parseaddr(msg['from'])[1]
                    subject = ''

                    if msg['subject']:
                        subject, encoding = email.header\
                            .decode_header(msg['subject'])[0]
                        if encoding:
                            subject = subject.decode(encoding)
                        # subject = subject.replace('\n', ' ').replace('\r', '')
                        if subject:
                            subject = str(subject).replace('|', '/')

                    print("%4d | %s | %-30s | %-40s | " % (count,
                                                           date,
                                                           sender[:30],
                                                           subject[:40]), end='')
                except TypeError as e:
                    print("Cannot read file %s" % path, file=sys.stderr)
            else:
                print("%sSubject: %s" % (offset * ' ', msg['subject']))
                print("%sDate: %s" % (offset * ' ', msg['date']))
                print("%sFrom: %s" % (offset * ' ', msg['from']))

    return offset


def list_messages(messages, mbox, root):
    count = 0

    for message_id in messages:
        count += 1

        offset = print_message(message_id,
                               os.path.join(root, mbox[message_id][0]),
                               count)
        if oneline:
            print(os.path.join(root, ' '.join(mbox[message_id])))
        else:
            for path in mbox[message_id]:
                print((offset + 2) * ' ' + path)


def list_differences(messages, L, R, lroot, rroot):
    count = 0

    for message_id in messages:
        count += 1
        offset = print_message(message_id,
                               os.path.join(lroot, L[message_id][0]),
                               count)
        if oneline:
            print(' (%s) <===> (%s)' % (' '.join(
                                            [get_mailbox_dir(l) for l in
                                             L[message_id]]),
                                        ' '.join(
                                            [get_mailbox_dir(r) for r in
                                             R[message_id]])))
        else:
            print((offset + 2) * ' ' + 7 * '<' + ' ' + lroot)
            for path in L[message_id]:
                print((offset + 2) * ' ' + path)
            print((offset + 2) * ' ' + 7 * '=')
            for path in R[message_id]:
                print((offset + 2) * ' ' + path)
            print((offset + 2) * ' ' + 7 * '>' + ' ' + rroot)


def index(messages, mbox, root):

    for key, message in mbox.iteritems():
        message_id = message['Message-Id']
        if message_id is None:
            # TODO: print warning or info
            continue

        location = os.path.relpath(os.path.join(mbox._path, mbox._toc[key]),
                                   root)
        try:
            if message_id in messages:
                messages[message_id].append(location)
            else:
                messages[message_id] = [location]
        except TypeError:
            pass

    for folder in mbox.list_folders():
        folder_mbox = mbox.get_folder(folder)
        if is_maildir(folder_mbox._path):
            print("Folder found: %s" % folder)
            index(messages, folder_mbox, root)
        elif verbose:
            print("Folder is not a valid Maildir: %s" % folder, file=sys.stderr)


def get_mailbox_dir(location):
    return os.path.relpath(os.path.join(os.path.dirname(location),
                                        os.path.pardir))


def diff(left, right, direction, lroot, rroot, quiet=False):
    L = {}
    R = {}

    for l in left:
        index(L, mailbox.Maildir(l), lroot)
    for r in right:
        index(R, mailbox.Maildir(r), rroot)

    if not quiet:
        print()

    uniqueL = [msg for msg in L if msg not in R]
    uniqueR = [msg for msg in R if msg not in L]
    different = [msg for msg in (m for m in L if m in R)
                 if set(get_mailbox_dir(l) for l in L[msg])
                 != set(get_mailbox_dir(r) for r in R[msg])]
    sum = len(uniqueL) + len(uniqueR) + len(different)

    if quiet:
        return sum
    elif sum == 0:
        print("No differences found between %s and %s." % (lroot, rroot))
        return sum

    if uniqueL and (direction == 'l' or direction == 'b'):
        print(79*'-')
        print("Only in %s:" % lroot)
        list_messages(uniqueL, L, lroot)

    if uniqueR and (direction == 'r' or direction == 'b'):
        print(79*'-')
        print("Only in %s:" % rroot)
        list_messages(uniqueR, R, rroot)

    if different and direction == 'b':
        print(79*'-')
        print("Different locations:")
        list_differences(different, L, R, lroot, rroot)

    return sum


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l",
                        "--left",
                        help="show only changes in left",
                        action="store_true")
    parser.add_argument("-r",
                        "--right",
                        help="show only changes in right",
                        action="store_true")
    parser.add_argument("-o",
                        "--oneline",
                        help="show metadata of mails in one line. Implies -v",
                        action="store_true")
    parser.add_argument("-q",
                        "--quiet",
                        help="Do not print output",
                        action="store_true")
    parser.add_argument("-v",
                        "--verbose",
                        help="show metadata of mails",
                        action="store_true")
    parser.add_argument("target_dirs", default=[], nargs="+")
    args = parser.parse_args()

    direction = 'b'
    if args.left and not args.right:
        direction = 'l'
    elif args.right and not args.left:
        direction = 'r'

    maildirs = args.target_dirs
    oneline = args.oneline
    quiet = args.quiet
    verbose = args.verbose or oneline

    if len(maildirs) != 2:
        print_usage(parser.prog)
        exit(1)

    left = get_maildirs(maildirs[0])
    right = get_maildirs(maildirs[1])

    changed = diff(left, right, direction, maildirs[0], maildirs[1], quiet)
    sys.exit(changed)
