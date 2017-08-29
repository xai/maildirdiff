# maildirdiff
Diff two maildirs recursively.

## Usage:
```maildirdiff.py [MAILDIR1] [MAILDIR2]```

## Example output:
```
maildirdiff.py INBOX Backup
--------------------------------------------------------------------------------
Only in ['INBOX']:
1. <8a18d8b8-2f03-d1ee-cca5-0ab73bb5b14e@example.org>
   Subject: Re: Meeting
   Date: Wed, 19 Jul 2017 16:22:29 +0200
   From: Some CoWorker <someone@example.org>
     /path/to/INBOX/cur/1500474151_0.2935.localhost,U=48773,FMD5=7e33429f656f1e6e9d79b29c3f82c57e:2,S
```
