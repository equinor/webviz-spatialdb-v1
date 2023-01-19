
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


class SurfaceModel:

    source_db = {
        "1": "OW",
        "2": "PetrelStudio"
    }

    COLORMAP_OPTIONS = {
    "1":"Physics",
    "2":"Rainbow",
    "3":"Porosity",
    "4":"Permeability",
    "6":"Time/Depth",
    "7":"Stratigraphy",
    "8":"Facies",
    "9":"GasOilWater",
    "10":"GasWater",
    "11":"OilWater",
    "12":"Accent",
    }

    @staticmethod
    def get_server_names(df):
        dfRes = df[['sourceProjectId','sourceDatabase']].drop_duplicates(
            subset=['sourceDatabase'], keep='last').set_index('sourceProjectId').sort_values(
            by=['sourceDatabase'])
        res = dfRes.to_dict()['sourceDatabase']
        return res

    @staticmethod
    def get_project_names(df):
        dfRes = df[['sourceProjectId', 'sourceProject']].sort_values(
            by=['sourceProject']).set_index('sourceProjectId')

        res = dfRes.to_dict()['sourceProject']
        return res

    @staticmethod
    def get_iset_names(df):
        dfRes = df[['interpretationSetId', 'interpretSetName']].sort_values(
            by=['interpretSetName']).set_index('interpretationSetId')
        res = dfRes.to_dict()['interpretSetName']
        return res

    @staticmethod
    def get_grid_names(df):
        dfRes = df[['gridId', 'surfaceName']].sort_values(
            by=['surfaceName']).set_index('gridId')
        res = dfRes.to_dict()['surfaceName']
        return res
