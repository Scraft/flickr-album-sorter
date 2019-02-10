#!/home2/gamesdev/python/venv/bin/python2.7
# -*- coding: utf-8 -*-
# Default python is part of system and we do not have access to install
# packages, so we have installed our own python for which we can install
# whatever modules we want, including flickr_api.

# Stop urllib failing with SSL error by using an update to date certificate
import os, keys
if keys.kSSL_CERT_FILE_REQUIRED:
    os.environ["SSL_CERT_FILE"] = keys.kSSL_CERT_FILE

import codecs
import sys

# Python normally detects console type, but it can't do this for the users
# web brower, so tell Python it is utf-8 (and make sure we specify that
# we are returning utf-8 data in our content-type header).
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# Direct errors to the browser
if keys.kDEBUGGING: 
    import cgitb
    cgitb.enable()

import utils
@utils.StaticVar("displayedHeader", False)
def PrintHttpContentheader():
    if PrintHttpContentheader.displayedHeader == False:
        print "Content-type: text/html;charset=utf-8\n"
        PrintHttpContentheader.displayedHeader = True

# When debugging, commenting this line in will allow errors to display,
# the main reason we don't have this always on is we can't do a HTTP
# redirect after we have set this line.
#PrintHttpContentheader()

import time
import httplib2
import urlparse
import requests
import Cookie
import datetime
import database
import utils
import urllib2

def GetCookies():
    # Get/build cookie for storing data between when we submit to Flickr's
    # authentication webpage and when it returns back to our script.
    cookie = None
    if "HTTP_COOKIE" in os.environ:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
    else:
        cookie = Cookie.SimpleCookie()

    return cookie

def HandleOauthRequestResponse(cookie):   
    oauth_verifier = parsed['oauth_verifier'][0]

    import flickr_api as f
    f.disable_cache()
    a = f.auth.AuthHandler.fromdict({
        'api_key' : keys.kAPI_KEY,
        'api_secret' : keys.kAPI_SECRET,
        'request_token_key' : cookie["request_token_key"].value,
        'request_token_secret' : cookie["request_token_secret"].value,
    })
    try:
        a.set_verifier(oauth_verifier)
        f.set_auth_handler(a)
    except urllib2.HTTPError as e:
        return HandleNotLoggedIn(cookie) 
    
    # Should be able to login now.
    user = utils.AutoRetry(f.test.login)

    # Add details to MySQL.
    token_id = database.AddToDatabase(user.id, a.access_token.key, a.access_token.secret)

    # Store userId in a cookie so we can attempt to avoid logging in next time.
    cookie["user_id"] = user.id
    cookie["token_id"] = token_id
    print cookie.output()

    # Can just display page now.
    HandlePage(user, token_id)
   
def HandlePage(user, token_id):

    # Now we have authenticated, we don't need our oauth request hanging around.
    cookie["request_token_key"] = None
    cookie["request_token_secret"] = None
    print cookie.output()

    # Once we have printed the header, we can start outputing.
    PrintHttpContentheader()

    buddyIconUrl = "http://flickr.com/buddyicons/%s.jpg" % (user.nsid)

    htmlStart = r"""
<head>
<link rel="stylesheet" href="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css" />
<script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
<script src="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
<script src="album-sorter.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body id="index">
<div style="align-items: center; display: flex;" data-role="header" data-position="fixed">
    <img id="buddyIcon" style="float:left;width:48px; height:48px; margin-top: 10px; margin-bottom: 10px; margin-left: 5px;" src='""" + buddyIconUrl + """' />
    <div style="align-items: baseline; display: flex; float: left;margin:0 0 0 5px">
        <div style="float:left;margin:0 0 0 5px"><h1 style="margin-top: 10px; margin-bottom: 10px;">Hello """ + user.username + r"""</h1></div>
        <div style="float:left;margin:0 0 0 15px; font-weight: 400;">Not you? <a href='javascript:document.location=%s""" % ('"') + keys.kCALLBACK_URL + """?action=signout"'>sign out</a></div>
    </div>
</div>
<div>
    <button style="float: left; width: 140px; margin-left: 25px;" class="ui-btn ui-btn-inline" id="button" data-user-id='""" + user.id + """' data-token-id='""" + str(token_id) + """'>Begin Sorting</button>
    <div style="margin-left: 140px; padding: 9px;" data-role="content"></div>
</div>
<div class="ui-checkbox">
    <label for="toggle_all" class="ui-btn ui-corner-all ui-btn-inherit ui-btn-icon-left ui-first-child ui-checkbox-off">
        <div style="width: 100%%; overflow: hidden;">
            <div style="width: 49%%; float: left;">Toggle All</div>
            <div style="margin-left: 51%%; font-weight: 400;" name="notUsed" id="toggleAllStatus"></div>
        </div>
    </label>
    <input type="checkbox" name="toggle_all" id="toggle_all" data-cacheval="true">
</div>
<form>
<fieldset data-role="controlgroup">
"""

    htmlRow = ur"""
<div class="ui-checkbox">
    <label for="%s" class="ui-btn ui-corner-all ui-btn-inherit ui-btn-icon-left ui-first-child ui-checkbox-off">
        <div style="width: 100%%; overflow: hidden;">
            <div style="width: 49%%; float: left;">%s</div>
            <div style="margin-left: 51%%; font-weight: 400;" name="status_message" id="%s"></div>
        </div>
    </label>
    <input type="checkbox" name="checkbox" id="%s" data-cacheval="true">
</div>
"""
    htmlEnd = r"""
</fieldset>
</form>  
</body>
    """

    print htmlStart

    photoSets = utils.AutoRetry(user.getPhotosets)
    for ix, photoSet in enumerate(photoSets):
        print htmlRow % ( photoSet.id, photoSet.title, photoSet.id, photoSet.id )
    print htmlEnd 

def HandleNotLoggedIn(cookie):
    import flickr_api as f
    f.disable_cache()
    
    authHandler = f.auth.AuthHandler(keys.kAPI_KEY, keys.kAPI_SECRET, callback=keys.kCALLBACK_URL)
    f.set_auth_handler(authHandler)
    url = authHandler.get_authorization_url("write")
    cookie["request_token_key"] = authHandler.request_token.key
    cookie["request_token_secret"] = authHandler.request_token.secret
    
    print cookie.output()
    print 'Location: %s\n' % (url)

def HandleResumeSession(cookie):
    token, secret = database.GetOAuthTokenAndSecret(cookie["user_id"].value, cookie["token_id"].value)
    if token == None or secret == None:
        return False
    
    import flickr_api as f
    f.disable_cache()
    a = f.auth.AuthHandler.fromdict({
        'api_key' : keys.kAPI_KEY,
        'api_secret' : keys.kAPI_SECRET,
        'access_token_key' : token,
        'access_token_secret' : secret,
    })
    try:
        f.set_auth_handler(a)
        HandlePage(f.test.login(), cookie["token_id"].value)
        return True
    except urllib2.HTTPError as e:
        pass
    
    return False
            
if __name__ == '__main__':
    try:
        # Cookies
        cookie = GetCookies()

        # Check URL to see if we have been passed parameters from Flickr.
        fullUrl = utils.GetFullUrl()
        parsed_path = urlparse.urlparse(fullUrl)
        parsed = urlparse.parse_qs(parsed_path.query)

        # If the user requests to sign out, we reload page and remove our stored user details
        signingOut = False
        if 'action' in parsed and parsed['action'][0] == 'signout':
            cookie['user_id'] = None
            cookie['token_id'] = None
            signingOut = True

        # If we already have a user_id and token_id, can we get a valid token from database and login with it.
        if not signingOut and "user_id" in cookie and "token_id" in cookie and HandleResumeSession(cookie):
            pass
        elif not signingOut and "oauth_verifier" in parsed and "oauth_token" in parsed and "request_token_key" in cookie and "request_token_secret" in cookie:
            HandleOauthRequestResponse(cookie)
        else:
            HandleNotLoggedIn(cookie)
    except:
        PrintHttpContentheader()
        raise