import yaml
import glob
import dropbox
import os

def loadConfig(file):
    with open(file, 'r') as stream:
        config_dict = yaml.safe_load(stream)
        return config_dict
        
def clearCache(path):
    files = glob.glob(path + '/*')
    for f in files:
        os.remove(f)

def fetchAndCacheSoundtrack(dropboxAccessToken, path):
    with dropbox.Dropbox(dropboxAccessToken) as dbx:
        # List available fiels
        files = dbx.files_list_folder(path='', include_non_downloadable_files=False)
        if len(files.entries) <= 0:
            raise Exception('No files found')

        # Select the last file in the folder
        fileToFetch = files.entries[-1]
        _, res = dbx.files_download(path='/' + fileToFetch.name)

        # Cache the fetched file
        cachedFilePath = path + '/' + fileToFetch.name
        with open(cachedFilePath, 'wb') as f:
            f.write(res.content)
            print('Soundtrack cached', cachedFilePath)

config = loadConfig('config.yaml')
print('Config loaded')

cachePath = config['cache_path']
clearCache(cachePath)
fetchAndCacheSoundtrack(config['dropbox_access_token'], cachePath)

cachedFiles = glob.glob(cachePath + '/*.mp3')
if len(cachedFiles) <= 0:
    raise Exception('Missing cached file. Exiting program.')

soundtrackPath = cachedFiles[0]
print('Ready using cached soundtrack', soundtrackPath)
