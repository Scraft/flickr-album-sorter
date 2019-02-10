import os, time
from flickr_api.flickrerrors import FlickrError, FlickrAPIError, FlickrServerError

def GetFullUrl():
    url = os.environ['HTTP_HOST']
    uri = os.environ['REQUEST_URI']
    return url + uri

def AutoRetry(f, *args, **kw):
    maxAttempts=5
    for attemptIx in range(maxAttempts):
        try:
            return f(*args, **kw)
        except (TypeError, FlickrError, FlickrAPIError, FlickrServerError):
            print "Hit TypeError from FlickR API",
            if attemptIx == maxAttempts - 1:
                print " raising"
                raise
            else:
                print " retrying (%d/%d)" % (attemptIx+1, maxAttempts)
                time.sleep(attemptIx)

def Dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

def StaticVar(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate           