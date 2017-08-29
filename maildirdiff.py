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

import email
import mailbox


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


def list_messages(messages, mbox):
    count = 0

    for message_id in messages:
        count += 1
        offset = (len(str(count)) + 2)

        print("%d. %s" % (count, message_id))

        with open(mbox[message_id][0], 'r',
                  encoding='utf-8',
                  errors='replace') as fp:
            msg = email.message_from_file(fp)
            print("%sSubject: %s" % (offset * ' ', msg['subject']))
            print("%sDate: %s" % (offset * ' ', msg['date']))
            print("%sFrom: %s" % (offset * ' ', msg['from']))

        for path in mbox[message_id]:
            print((offset + 2) * ' ' + path)


def index(messages, mbox):

    for key, message in mbox.iteritems():
        message_id = message['Message-Id']
        if message_id is None:
            # TODO: print warning or info
            continue

        if message_id in messages:
            messages[message_id].append(mbox._path + os.sep + mbox._toc[key])
        else:
            messages[message_id] = [mbox._path + os.sep + mbox._toc[key]]

    for subdir in mbox.list_folders():
        print("Subdir found: %s", subdir)
        index(messages, subdir)


def diff(left, right):
    L = {}
    R = {}

    for l in left:
        print("Indexing " + l)
        index(L, mailbox.Maildir(l))
    for r in right:
        print("Indexing " + r)
        index(R, mailbox.Maildir(r))

    print()

    uniqueL = [msg for msg in L if msg not in R]
    uniqueR = [msg for msg in R if msg not in L]

    if not uniqueL and not uniqueR:
        print("No differences found.")
        return

    if uniqueL:
        print(80*'-')
        print("Only in %s:" % left)
        list_messages(uniqueL, L)

    if uniqueR:
        print(80*'-')
        print("Only in %s:" % right)
        list_messages(uniqueR, R)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target_dirs", default=[], nargs="+")
    args = parser.parse_args()

    maildirs = args.target_dirs

    if len(maildirs) != 2:
        print_usage(parser.prog)
        exit(1)

    left = get_maildirs(maildirs[0])
    right = get_maildirs(maildirs[1])

    diff(left, right)
