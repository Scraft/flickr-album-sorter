# flickr-album-sorter
Sort flickr albums into date taken order

# Installation
You will need to update the keys.py file to set up various settings:
* kAPI_KEY/kAPI_SECRET : the app API key/secret for your flickr app
* kDATABASE_HOST, kDATABASE_DATABASE, kDATABASE_USER, kDATABASE_PASSWORD : MySQL database host/table/user/password
* kCALLBACK_URL : the URL the script is being hosted
* kSSL_CERT_FILE_REQUIRED, kSSL_CERT_FILE : if a custom CA Cert is required for the webserver to access SSL sites
* kDEBUGGING : set to true for more debug info

It needs to be pointed to a MySQL database which is set up as:
* token_id, Primary key, int(10), UNSIGNED
* oauth_token, text
* oauth_token_secret, text
* user_id,	text

Other bits:
* The scripts auth-test.py and sort-album.py need to be set as executable (CHMOD 755).
* Your webserver may need to be setup to ensure Python is used to execute .py scripts (which can be done via .htaccess with Apache).
* The path to Python needs to be setup on the shebang (first line) of auth-test.py and sort-album.py
* There are a few Python dependencies, flickr-api being one; I can't remember the others off hand, but hopefully the errors will be obvious - feel free to do a pull request to update this README with the actual dependency list!
