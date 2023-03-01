
######################################################################
#
# Business logic is intended to possess data handling functionality
# separated from GUI code, i.e.separated from Dash-related code
# and visualization format (e.g. plotly when graphing data)
#
# Rule: No dash* import allowed
#
# Query database/input for relevant data and necessary ad-hoc
# calculations for data.
#
######################################################################

import os
import requests
import pandas as pd


class SurfaceModel:

    source_db = {
        "1": "OW",
        "2": "PetrelStudio"
    }

    COLORMAP_OPTIONS = {
        "1": "Rainbow",
        "2": "Physics",
        "3": "Porosity",
        "4": "Permeability",
        "6": "Time/Depth",
        "7": "Stratigraphy",
        "8": "Facies",
        "9": "GasOilWater",
        "10": "GasWater",
        "11": "OilWater",
        "12": "Accent",
    }

    @staticmethod
    def get_user_project(token, projects_df):
        GRAPH_GROUP_URL = os.environ["GRAPH_GROUP_URL"]
        api_result = requests.get(  # Use token to call downstream api
            GRAPH_GROUP_URL,
            headers={'Authorization': 'Bearer ' + token},
        ).json()

        projects_df.objectId = projects_df.objectId.str.split(',')
        projects_df = projects_df.explode('objectId')

        df = pd.json_normalize(api_result['value'])

        df = df.rename(columns={"id": "objectId"})
        df=df[['objectId']]
        df_res = pd.merge(df, projects_df, on='objectId')
        return df_res

    @staticmethod
    def get_server_names(df):
        df = df[['sourceProjectId', 'sourceDatabase']].drop_duplicates(
            subset=['sourceDatabase'], keep='last')
        res = df.to_dict(orient='records')
        options = [{'label': i['sourceDatabase'], 'value': i['sourceProjectId']}
                   for i in res]
        sorted_options = sorted(options, key=lambda x: x["label"])
        return sorted_options

    @staticmethod
    def get_project_names(df):
        res = df.to_dict(orient='records')
        options = [{'label': i['sourceProject'], 'value': i['sourceProjectId']}
                   for i in res]
        sorted_options = sorted(options, key=lambda x: x["label"])
        return sorted_options

    @staticmethod
    def get_iset_names(df):
        res = df.to_dict(orient='records')
        options = [{'label': i['interpretSetName'], 'value': i['interpretationSetId']}
                   for i in res]
        sorted_options = sorted(options, key=lambda x: x["label"])
        return sorted_options

    @staticmethod
    def get_grid_names(df):
        res = df.to_dict(orient='records')
        options = [{'label': i['surfaceName'] + " (GRID_ID: " + str(i['gridId']) + ')', 'value': i['gridId']}
                   for i in res]
        sorted_options = sorted(options, key=lambda x: x["label"])
        return sorted_options
