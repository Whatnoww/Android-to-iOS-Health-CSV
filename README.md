# Android to iOS Health CSV

This set of scripts, pulls your CSV files generated from Health Sync Android (https://play.google.com/store/apps/details?id=nl.appyhapps.healthsync&hl=en-us), converts them to Health CSV Importer iOS (https://apps.apple.com/us/app/health-csv-importer/id1275959806) compatible files and reuploads them combined to a drive folder of choice via folder_ID. It does some versioning, so you can run it whenever you like then sync the new output file without duplicates in theory.

## Running
You can probably automate this, it'll check for an internet connection if you start execution from internetcheck.py, everything else runs in sequence.

You can also run this manually by removing the upload.py and starting execution from convert_sleep_csvs.py. You can just place the generated files from Health Sync Android in the input_csvs folder. This will allow you to skip having to get dev keys and such. You'll need an oauth credentials file you can get from the Google Developer Console to automate the drive portion of this script.

## Limitations
Don't know how to automate ingest on the iOS side. Still looking for a way to automate it using Shortcuts.

I have found a workaround of sorts. I task the job to run at a given time, Nextcloud syncs the file to a folder, and on iOS I have a shortcut that grabs the file from a public share in Nextcloud (you left click the Download button after sharing the csv, it seems to retain the same url regardless of file updates) and then opens it in CSV import, which works.

![image](https://github.com/user-attachments/assets/c4b0fcc4-308e-4344-9f30-8f29e07600ef)



## Warning
I offer zero support. I just wanted a way to automate moving my sleep data (and hopefully everything else) from my Android device to my iOS device.
