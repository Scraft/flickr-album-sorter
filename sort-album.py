#!/home2/gamesdev/python/venv/bin/python2.7
# -*- coding: utf-8 -*-

import os, keys
if keys.kSSL_CERT_FILE_REQUIRED:
    os.environ["SSL_CERT_FILE"] = keys.kSSL_CERT_FILE
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
if keys.kDEBUGGING: 
    import cgitb
    cgitb.enable()
import urlparse
import utils
import database
import datetime
import json

def CreateReturnJson(success, message):
    return json.dumps( { 
        "result" : ["error","success"][success], 
        ["error_message","message"][success] : message
    } )   

if __name__ == '__main__':
    print "Content-type: text/html;charset=utf-8\n"

    fullUrl = utils.GetFullUrl()
    parsed_path = urlparse.urlparse(fullUrl)
    parsed = urlparse.parse_qs(parsed_path.query)

    oauth_token, oauth_token_secret = database.GetOAuthTokenAndSecret(parsed['userId'][0], parsed['tokenId'][0])
    import flickr_api as f
    f.disable_cache()

    f.set_auth_handler(f.auth.AuthHandler.fromdict({
        'api_key' : keys.kAPI_KEY,
        'api_secret' : keys.kAPI_SECRET,
        'access_token_key' : oauth_token,
        'access_token_secret' : oauth_token_secret,
    }))
    user = utils.AutoRetry(f.test.login)
    photoSets = utils.AutoRetry(user.getPhotosets)
    photoSet = next((x for x in photoSets if x.id == parsed['albumId'][0]), None)
    if photoSet == None:
        print CreateReturnJson(False, "Invalid photoset ID")
    else:
        photos = utils.AutoRetry(photoSet.getPhotos, extras='date_taken')
        for i in range(photos.info.page + 1, photos.info.pages + 1):
            photos += utils.AutoRetry(photoSet.getPhotos, page=i, extras='date_taken')

        sortedPhotos = []
        for photo in photos:
            dt = datetime.datetime.strptime(photo.datetaken, '%Y-%m-%d %H:%M:%S')
            sortedPhotos.append({ "photo" : photo, "taken" : dt })

        sortedPhotos = sorted(sortedPhotos, key=lambda k: k['taken']) 
        orderedIds = [d['photo'].id for d in sortedPhotos]
        if orderedIds == [d.id for d in photos]:
            print CreateReturnJson(True, "Done (already in order)")
        else:
            photoSet.reorderPhotos(photo_ids = orderedIds)  
            print CreateReturnJson(True, "Done")          