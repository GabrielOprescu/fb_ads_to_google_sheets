This project is useful to get campaigns data from Facebook Ads and store them in a sheet in Google Drive.

The end purpose it to create a dashboard in Looker where data sources like Facebook Ads, Google Ads, Google Analytics and others, will be combined.

To get access to Facebook Ads data, you will first need to have an ads account where you are admin.

Next generate an API in Facebook. The API will generated a series of secret information that you will store in /env/.local file. Take a look to see the necessary info.

For Google you need to create an API in Google Cloud. Through that API you will gain access to Google Sheets. The API will generate credentials stored in ./env/credentials.json. With the credentials, using gd_extract_credentials functions, a ./env/token.json is generated. With the token you can read and write data from Google Sheets. 

Once you have all the access details are generated and placed in the ./env folder, just run update_sheet.py.

In update_sheet, thre are FB_FIELDS and FB_PARAMS are of my own choice. You can select your owns. The function fb_get_day_insights has all the documentation needed.

Also, make sute the Google Sheet that you want to update or change has the necessary headers.