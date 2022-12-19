import os
from datetime import datetime, timedelta
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1SJTE2-DpOpTpfWWN_VbsSxUtEiQPdGVAPhxzEDQ9YXA"
SAMPLE_RANGE_NAME = "Class Data!A2:E2"


def gd_extract_credentials(credentials: str, scopes: str) -> None:
    """Utility to extract from Google Cloud the token needed to access the drive.
    A file called token.json will be generated.
    For more info, go here: https://developers.google.com/drive/api/quickstart/python

    Args:
        credentials: a json file with credentials generated by the API on Google cloud.
        scopes (str): what kind of access to allow: read, write, all.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(
                spreadsheetId="1SJTE2-DpOpTpfWWN_VbsSxUtEiQPdGVAPhxzEDQ9YXA",
                range="Class Data!A2:E2",
            )
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Name, Major:")
        for row in values:
            print("%s, %s" % (row[0], row[4]))
    except HttpError as err:
        print(err)


def gd_get_values(
    spreadsheet_id: str, range_name: str, major_dim: str, token: str
) -> dict:
    """Function to extract a certain range of values from spreadsheet.
    More info can be found here: https://developers.google.com/sheets/api/guides/values

    Args:
        spreadsheet_id (str): id of the spreadsheet
        range_name (str): A:X / A4:C8 / A:A
        major_dim (str): how to extract data, by columns or rows: COLUMNS / ROWS
        token (str): path to the json file generated with the function gd_extract_credentials

    Returns:
        dict: several key to describe the data
    """
    # connect ot the api
    creds = Credentials.from_authorized_user_file(token)

    try:
        service = build("sheets", "v4", credentials=creds)

        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id, range=range_name, majorDimension=major_dim
            )
            .execute()
        )

        rows = result.get("values", [])

        print(f"{len(rows)} rows retrieved")

        return result

    except HttpError as error:

        print(f"An error occurred: {error}")

        return error


def gd_update_values(
    spreadsheet_id: str,
    range_name: str,
    value_input_option: str,
    values: list[list],
    token: str,
) -> None:
    """Function to update values in a certain range from spreadsheet.
    More info can be found here: https://developers.google.com/sheets/api/guides/values

    Args:
        spreadsheet_id (str): id of the spreadsheet
        range_name (str): A:X / A4:C8 / A:A
        value_input_option (str): to parse or not the values (RAW / USER_ENTERED)
        major_dim (str): how to extract data, by columns or rows: COLUMNS / ROWS
        values (list): a list of lists with values that will be placed in the range
        token (str): path to the file generated with the function gd_extract_credentials

    Returns:
        None
    """
    creds = Credentials.from_authorized_user_file(token)

    try:

        service = build("sheets", "v4", credentials=creds)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def gd_append_values(
    spreadsheet_id: str,
    value_input_option: str,
    range_name: str,
    values: list[list],
    token: str,
) -> None:
    """Function to append values in a certain range from spreadsheet.
    More info can be found here: https://developers.google.com/sheets/api/guides/values

    Args:
        spreadsheet_id (str): id of the spreadsheet
        range_name (str): A:X / A4:C8 / A:A
        value_input_option (str): to parse or not the values (RAW / USER_ENTERED)
        major_dim (str): how to extract data, by columns or rows: COLUMNS / ROWS
        values (list): a list of lists with values that will be placed in the range
        token (str): path to the file generated with the function gd_extract_credentials

    Returns:
        None
    """
    creds = Credentials.from_authorized_user_file(token)

    try:

        service = build("sheets", "v4", credentials=creds)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                valueInputOption=value_input_option,
                body=body,
                range=range_name,
            )
            .execute()
        )
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def fb_get_day_insights(
    min_date: str,
    max_date: str,
    access_token: str,
    fields: list,
    params: dict,
    ad_account_id: str,
) -> dict:
    """This is a function for downloading insights at a dayly basis.
    More informations here: https://developers.facebook.com/docs/marketing-api/insights

    Args:
        min_date (str): starting date for extraction
        max_date (str): ending date for extraction
        access_token (str): the token taken from facebook api platform. first create an app
        fields (list): what information to extract: campaign_name, impressions, cpc ...
        params (dict): adtional information regarding time rage, splits , info ...
        ad_account_id (str): the id of the ads account in the shape of act_123456789

    Raises:
        ValueError: the fields parameter is not a list
        ValueError: the params parameter is not a dict
        ValueError: max_date > min_date

    Returns:
        dict: a list of dictionaries containing metrics for a campaign
    """

    # initialize the api with the token
    FacebookAdsApi.init(access_token=access_token)

    if not isinstance(fields, list):
        raise ValueError("Fields must be list")

    if not isinstance(params, dict):
        raise ValueError("Params must be dict")

    if params.get("time_range") is not None:
        print(
            "Info: Time_range key from params will be updated using min_date and max_date\n"
        )

    min_date = datetime.strptime(min_date, "%Y-%m-%d")
    print(f"Minimum date is {min_date}")
    max_date = datetime.strptime(max_date, "%Y-%m-%d")
    print(f"Maximum date is {max_date}")

    diff_days = (max_date - min_date).days

    if diff_days < 0:
        raise ValueError("Max_date must be greater or equal with min_date")

    print(f"A total of {diff_days} days will be extracted")

    item_list = []

    for i in range(diff_days + 1):
        since = until = (min_date + timedelta(days=i)).strftime("%Y-%m-%d")

        print(f"Taking day of {since}")

        params["time_range"] = {"since": since, "until": until}

        response = AdAccount(ad_account_id).get_insights(fields=fields, params=params)

        for resp in response:
            item_list.append(resp._json)

    return item_list
