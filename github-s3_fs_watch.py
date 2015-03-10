#!/usr/bin/python
'''
File system watcher is a script that runs on Linux systems, which will watch
a specified directory(WATCHED_PATH), on a IN_CLOSE_WRITE(iNotify) event
   https://www.kernel.org/pub/linux/kernel/people/rml/inotify/headers/inotify.h
the script will upload the target file to a S3 bucket hosted on AWS(S3_BUCKET)

Requirements
-----
Python libs
 - pyinotify
 - boto

Linux:
 - Kernel 2.6.13+

Supported iNotify events    
 - IN_CREATE
 - IN_CLOSE_WRITE
'''
import pyinotify
import os
import sys
import boto.s3
from time import sleep
from boto.s3.key import Key
#-----------------------------------------------------------------------------------
# GLobal Vars #
IAM_PROFILE = True
S3_BUCKET = ""
WATCHED_PATH = ""

# If IAM role set to False
REGION_NAME = "us-west-1"
#-----------------------------------------------------------------------------------
def get_s3_connection():
    '''Return a connection object to S3 buckets'''
    if IAM_PROFILE:
        return boto.s3.connection.S3Connection()
    else:
        return boto.s3.connect_to_region(REGION_NAME)

#-----------------------------------------------------------------------------------
def get_s3_bucket(s3_connection):
    ''' Return a s3 bucket'''
    return s3_connection.get_bucket(S3_BUCKET)

#-----------------------------------------------------------------------------------
class Events(pyinotify.ProcessEvent):
    '''Events class, handle all supported events'''
    def __init__(self):
        pass

    def process_IN_CREATE(self, event):
        # TODO: On folder creation, create stub in S3'''
        if os.path.isdir(event.pathname):
            pass
                
    def process_IN_CLOSE_WRITE(self, event):
        '''Upload file on CLOSE_WRITE event to S3'''
        filename = event.pathname.replace(WATCHED_PATH, '/')

        # Sleep just incase a transient file
        sleep(5)

        # Only handle files, ignore folders
        # IN_CREATE will handle folder creations
        if os.path.isfile(event.pathname):

            print "Uploading file %s" % event.pathname

            # Create connection to AWS S3
            conn = get_s3_connection()
            buckets = get_s3_bucket(conn)

            # Start the S3 upload
            key = Key(buckets)
            key.key = filename
            key.set_contents_from_filename(event.pathname)

        # TODO: Check and ensure that file has been uploaded S3

#-----------------------------------------------------------------------------------
def main():
    '''Launch Notifier and start watching'''

    print "Starting watcher, watching path: %s" % WATCHED_PATH

    # List of supported iNotify events
    events = pyinotify.IN_CREATE | \
             pyinotify.IN_CLOSE_WRITE

    watcher = pyinotify.WatchManager()

    notifier = pyinotify.Notifier(watcher, Events())
    watcher.add_watch(WATCHED_PATH, events, rec=True)

    while True:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()

#-----------------------------------------------------------------------------------
if __name__ == "__main__":
    '''
    On program load, call main, as we are in an infinite loop, look for
    SIGINT and catch, to ensure a clean exit
    '''
    try:
        main()
    except KeyboardInterrupt:
        print "Exiting"
        sys.exit(0)
