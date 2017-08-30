# maildirdiff
Diff two maildirs recursively.

## Usage:
```maildirdiff.py [-l] [-r] [-v] MAILDIR1 MAILDIR2```

`-l` Show only changes in left maildir  
`-r` Show only changes in right maildir  
`-o` Compact oneline output, implies -v  
`-v` Show metadata of mails

## Example output:
Normal run:
```
maildirdiff.py INBOX Backup
--------------------------------------------------------------------------------
Only in INBOX:

1. <8a18d8b8-2f03-d1ee-cca5-0ab73bb5b14e@example.org>
     INBOX/cur/1500474151_0.2935.localhost,U=48773,FMD5=7e33429f656f1e6e9d79b29c3f82c57e:2,S
```
Run with verbose output:
```
maildirdiff.py -v INBOX Backup
--------------------------------------------------------------------------------
Only in INBOX:

1. <8a18d8b8-2f03-d1ee-cca5-0ab73bb5b14e@example.org>
   Subject: Re: Meeting
   Date: Wed, 19 Jul 2017 16:22:29 +0200
   From: Some CoWorker <someone@example.org>
     INBOX/cur/1500474151_0.2935.localhost,U=48773,FMD5=7e33429f656f1e6e9d79b29c3f82c57e:2,S
```
Run with oneline output:
```
maildirdiff.py -o INBOX Backup
--------------------------------------------------------------------------------
Only in INBOX:
   1 | 2017-07-19 16:22 | someone@example.org | Re: Meeting         | INBOX/cur/1500474151_0.2935.localhost,U=48773,FMD5=7e33429f656f1e6e9d79b29c3f82c57e:2,S
```
