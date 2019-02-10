# flickr-album-sorter
Sort flickr albums into date taken order

# Installation
You will need to update the keys.py file to set up various settings:
kAPI_KEY/kAPI_SECRET : the app API key/secret for your flickr app
kDATABASE_HOST, kDATABASE_DATABASE, kDATABASE_USER, kDATABASE_PASSWORD : MySQL database host/table/user/password
kCALLBACK_URL : the URL the script is being hosted
kSSL_CERT_FILE_REQUIRED, kSSL_CERT_FILE : if a custom CA Cert is required for the webserver to access SSL sites
kDEBUGGING : set to true for more debug info

It needs to be pointed to a MySQL database which is set up as:
token_id, Primary key, int(10), UNSIGNED
oauth_token, text
oauth_token_secret, text
user_id,	text
