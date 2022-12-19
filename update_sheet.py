"""
For this script to work, first generate the credentials, token from google drive and the token, secret and app id from facebook 
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils import gd_get_values, gd_update_values, gd_append_values, fb_get_day_insights

load_dotenv("./env/.local", override=True)

# facebook info
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
FB_AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_APP_ID = os.getenv("FB_APP_ID")

FB_FIELDS = [
    "campaign_name",
    "impressions",
    "cpc",
    "ctr",
    "reach",
    "actions",
    "cost_per_action_type",
    "spend",
]
FB_PARAMS = {
    "time_range": {"since": "2022-10-26", "until": "2022-10-26"},
    "filtering": [
        {"field": "campaign.delivery_info", "operator": "IN", "value": ["active"]}
    ],
    "level": "campaign",
    # 'breakdowns': ['gender'],
}

# If modifying these scopes, delete the file token.json.
GD_SCOPES = [os.getenv("GD_SCOPES")]
GD_SPREADSHEET_ID = os.getenv("GD_SPREADSHEET_ID")


def main():

    # get the actual data from drive to see the latest date

    full_sheet = gd_get_values(GD_SPREADSHEET_ID, "A:L", "COLUMNS", "./env/token.json")

    dt_lst = [l[1:] for l in full_sheet["values"] if l[0] == "date_start"][0]

    if len(dt_lst) == 0:
        latest_gd_date = (datetime.now() - timedelta(days=92)).strftime("%Y-%m-%d")
    else:
        latest_gd_date = (
            datetime.strptime(max(dt_lst), "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")

    if latest_gd_date == datetime.now().strftime("%Y-%m-%d"):
        print("Everything is up to date")
        exit()

    actual_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # get the data from facebook with corresponding dates
    item_list = fb_get_day_insights(
        min_date=latest_gd_date,
        max_date=actual_date,
        access_token=FB_ACCESS_TOKEN,
        ad_account_id=FB_AD_ACCOUNT_ID,
        fields=FB_FIELDS,
        params=FB_PARAMS,
    )

    # format the data in a easy to make other objects form
    accepted_metrics = [
        "campaign_name",
        "impressions",
        "cpc",
        "ctr",
        "reach",
        "link_click",
        "landing_page_view",
        "spend",
        "date_start",
        "date_stop",
    ]
    recorded_metrics = [
        "campaign_name",
        "impressions",
        "cpc",
        "ctr",
        "reach",
        "link_click_actions",
        "landing_page_view_actions",
        "link_click_cost",
        "landing_page_view_cost",
        "spend",
        "date_start",
        "date_stop",
    ]

    campaign_list = []

    for campaign in item_list:

        tmp_dct = {}

        for k, v in campaign.items():
            if k == "actions":
                for l in v:
                    if l["action_type"] in accepted_metrics:
                        tmp_lst = list(l.values())
                        tmp_dct[tmp_lst[0] + "_actions"] = float(tmp_lst[1])
            elif k == "cost_per_action_type":
                for l in v:
                    if l["action_type"] in accepted_metrics:
                        tmp_lst = list(l.values())
                        tmp_dct[tmp_lst[0] + "_cost"] = float(tmp_lst[1])
            else:
                if k in ("impressions", "cpc", "ctr", "reach", "spend"):
                    tmp_dct[k] = float(v)
                else:
                    tmp_dct[k] = v

            tmp_dct_sort = {}
            for v in recorded_metrics:
                if v in tmp_dct.keys():
                    tmp_dct_sort[v] = tmp_dct[v]
                else:
                    tmp_dct_sort[v] = 0

        campaign_list.append(tmp_dct_sort)

    # make a list of list from list of dict
    input_list = [list(item.values()) for item in campaign_list]

    # push values to spreadsheet
    gd_append_values(
        spreadsheet_id=GD_SPREADSHEET_ID,
        value_input_option="RAW",
        range_name="A:L",
        values=input_list,
        token="./env/token.json",
    )


if __name__ == "__main__":
    main()
