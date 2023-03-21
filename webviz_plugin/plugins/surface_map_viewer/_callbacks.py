
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from dash import ALL, MATCH, Input, Output, State, callback, callback_context, no_update
import xtgeo
from ._layer_model import DeckGLMapLayersModel
from ._business_logic import SurfaceModel
from ._layout import LayoutElements
import flask

from .surface_array_server import SurfaceArrayServer, QualifiedSurfaceAddress, SimulatedSurfaceAddress

from azure.storage.filedatalake import (
    FileSystemSasPermissions,
    generate_file_system_sas,
)
from datetime import datetime, timedelta


###########################################################################
#
# Collection of Dash callbacks.
#
# The callback functions should retreive Dash Inputs and States, utilize
# business logic and props serialization functionality for providing the
# JSON serializable Output for Dash properties callbacks.
#
# The callback Input and States should be converted from JSON serializable
# formats to strongly typed and filtered formats. Furthermore the callback
# can provide the converted arguments to the business logic for retreiving
# data or performing ad-hoc calculations.
#
# Results from the business logic is provided to the props serialization to
# create/build serialized data formats for the JSON serializable callback
# Output.
#
###########################################################################

df_user_projects = pd.DataFrame()


def plugin_callbacks(get_uuid: Callable, iset_names: pd.DataFrame, sever_names: pd.DataFrame, grid_names: pd.DataFrame, surface_server: SurfaceArrayServer):

    @callback(
        [
            Output('image', 'src'),
            Output('divimg', 'style'),
            Output('divdeck', 'style'),
            Output(get_uuid(LayoutElements.DECKGLMAP), "layers"),
            Output(get_uuid(LayoutElements.DECKGLMAP), "views"),
            Output(get_uuid(LayoutElements.COLOURMAP_DROPDOWN), "disabled"),
        ],
        [
            Input(get_uuid(LayoutElements.COLOURMAP_DROPDOWN), "value"),
            Input(get_uuid(LayoutElements.QUICKLOAD_OPTION), "value"),
            Input(get_uuid(LayoutElements.GRID_DROPDOWN), "value"),
            State(get_uuid(LayoutElements.SERVER_DROPDOWN), "value"),
            State(get_uuid(LayoutElements.SERVER_DROPDOWN), "options"),
            State(get_uuid(LayoutElements.PROJECT_DROPDOWN), "value"),
            State(get_uuid(LayoutElements.PROJECT_DROPDOWN), "options"),
            State(get_uuid(LayoutElements.ISET_DROPDOWN), "value"),
        ],
    )
    def _update_map(
        colour_value: str, quickload_value: str, grid_value: str, server_value: str, server_options: dict, project_value: str, project_options: dict, iset_value: str
    ) -> tuple:

        layers: List[Dict] = []
        sas_url = ''
        map_bounds = []
        layersid = []
        map_views = []
        divimg = {'display': 'none',  "flex": "2"}
        divdeck = {'display': 'block',  "flex": "2"}

        if quickload_value == '1':
            colour_disabled = True
        else:
            colour_disabled = False

        if grid_value:
            df_server = pd.DataFrame(server_options)
            df_server_out = df_server.loc[df_server['value'] == server_value]
            server = df_server_out.iloc[0]['label']

            df_project = pd.DataFrame(project_options)
            df_project_out = df_project.loc[df_project['value']
                                            == project_value]
            project = df_project_out.iloc[0]['label']

            relatie_path = server+"_" + project + "/"

            grid_data = grid_names.loc[(grid_names['gridId'] == (grid_value)) & (
                grid_names['sourceProjectId'] == int(project_value))]
            if iset_value:
                grid_data = grid_data.loc[(
                    grid_data['interpretationSetId'] == int(iset_value))]

            json_dict = grid_data.iloc[0]
            source_grid_id = str(json_dict['sourceGridId'])

            if quickload_value == '1':
                img_path = 'SpatialDB/processed/surface_coordinates/' + relatie_path + 'images/' + \
                    source_grid_id + '.png'
                sas_url = SurfaceModel.get_sas_token(img_path)

                divimg = {'display': 'block',  "flex": "2"}
                divdeck = {'display': 'none',  "flex": "2"}
            else:
                layersid = [LayoutElements.AXES_LAYER,
                            LayoutElements.MAP_LAYER]

                z_path = "SpatialDB/processed/surface_coordinates/" + \
                    relatie_path + source_grid_id + ".parquet"
                z_sas_url = SurfaceModel.get_sas_token(z_path)
                colormapname = SurfaceModel.COLORMAP_OPTIONS[colour_value]
                ncol, nrow = json_dict['NCOL'], json_dict['NROW']
                xori, yori = float(json_dict['XORI']), float(json_dict['YORI'])
                xinc, yinc = float(json_dict['XINC']), float(json_dict['YINC'])
                rotation = float(json_dict['ROTATION'])

                df = pd.read_parquet(z_sas_url)

                values = df['z'].to_numpy(copy=True)
                values = values*-1
                values = np.reshape(values, (nrow, ncol)).astype(np.float32)
                values = np.transpose(values)

                # ncol, nrow = nrow, ncol  # note flip on ncol/nrow definition
                depth_surface = xtgeo.RegularSurface(ncol=ncol, nrow=nrow,
                                                     xori=xori, yori=yori,
                                                     xinc=xinc, yinc=yinc, rotation=rotation,
                                                     values=values)
                surface_address = SimulatedSurfaceAddress(
                    attribute=grid_value,
                    name=json_dict['surfaceName'],
                    datestr="",
                    realization=100,
                )
                qualified_address = QualifiedSurfaceAddress(
                    'provider_id', surface_address)
                surface_server.publish_surface(
                    qualified_address, depth_surface)
                url = surface_server.encode_partial_url(qualified_address)
                map_bounds = [
                    depth_surface.xmin,
                    depth_surface.ymin,
                    -np.nanmax(depth_surface.values),
                    depth_surface.xmax,
                    depth_surface.ymax,
                    np.nanmin(depth_surface.values),
                ]
                layers.extend([
                    {
                        "@@type": "AxesLayer",
                        "id": LayoutElements.AXES_LAYER,
                        "bounds": map_bounds,
                    },
                    {
                        "@@type": "MapLayer",
                        "id": LayoutElements.MAP_LAYER,
                        "meshUrl": url,
                        "frame": {
                            "origin": [depth_surface.xori, depth_surface.yori],
                            "count": [depth_surface.ncol, depth_surface.nrow],
                            "increment": [depth_surface.xinc, depth_surface.yinc],
                            "rotDeg": depth_surface.rotation,
                        },
                        "contours": [0, 20],
                        "isContoursDepth": True,
                        "gridLines": False,
                        "material": True,
                        "colorMapName": colormapname,
                        "name": "mesh",
                    },
                ])

                divimg = {'display': 'none',  "flex": "2"}
                divdeck = {'display': 'block',  "flex": "2"}

        map_views = {
            "layout": [1, 1],
            "showLabel": False,
            "viewports": [
                {
                    "id": "deck_view",
                    "show3D": False,
                    "layerIds": layersid,
                    "isSync": True,
                },
            ],
        }

        return (sas_url, divimg, divdeck, layers,   map_views, colour_disabled)

# SET SERVER START

    @callback(
        [
            Output(get_uuid(LayoutElements.SERVER_DROPDOWN), "value"),
            Output(get_uuid(LayoutElements.SERVER_DROPDOWN), "options"),
        ],
        [
            Input(get_uuid(LayoutElements.SOURCE_DB_DROPDOWN), "value")
        ],
    )
    def _set_server(
        source_db_value: str

    ) -> dict:
        db_name = SurfaceModel.source_db[source_db_value]
        server_names_fil = sever_names.loc[sever_names['source']
                                           == (db_name)]
        global df_user_projects

        if 'localhost' in flask.request.url:
            token = 'eyJ0eXAiOiJKV1QiLCJub25jZSI6Im41V0NWV1FudnBOQTROTi1DUi14Mkd5UGl5MVZVMkY0ZmlVbndGYlcwQ0kiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8zYWE0YTIzNS1iNmUyLTQ4ZDUtOTE5NS03ZmNmMDViNDU5YjAvIiwiaWF0IjoxNjc5Mzc2NDExLCJuYmYiOjE2NzkzNzY0MTEsImV4cCI6MTY3OTM4MDc4NiwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsidXJuOnVzZXI6cmVnaXN0ZXJzZWN1cml0eWluZm8iXSwiYWlvIjoiQVRRQXkvOFRBQUFBaUxBelkwM3FFdjlFeGdLNHFVK0NwWEJoRmVyZGdvc3Y2OTdQT3plYUhsR0drcUFjdVRtQ0RkcldncmE5dmcwUyIsImFtciI6WyJwd2QiXSwiYXBwX2Rpc3BsYXluYW1lIjoicmFkaXgtd2Vidml6LXNwYXRpYWxkYiIsImFwcGlkIjoiNTI0N2ZmMGEtOGRjZS00ZjM4LThmY2YtNzFlNWE4YTRjMzY4IiwiYXBwaWRhY3IiOiIxIiwiZmFtaWx5X25hbWUiOiJLaGFtcmFpIiwiZ2l2ZW5fbmFtZSI6IlN1cmFqaXQiLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiOiI1MS4xMy42OC45OCIsIm5hbWUiOiJTdXJhaml0IEtoYW1yYWkgKFRhdGEgQ29uc3VsdGFuY3kgU2VydmljZXMgTGltaSkiLCJvaWQiOiIyMjJhZmZiYS0wM2FjLTQxOTQtYTg1OS0xOGVkNmI3ZjZiYWMiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMjIwNTIzMzg4LTEwODUwMzEyMTQtNzI1MzQ1NTQzLTI2MzQwNTMiLCJwbGF0ZiI6IjMiLCJwdWlkIjoiMTAwMzIwMDFCMkZCMzk5RiIsInJoIjoiMC5BUUlBTmFLa091SzIxVWlSbFhfUEJiUlpzQU1BQUFBQUFBQUF3QUFBQUFBQUFBQUNBRlEuIiwic2NwIjoiZW1haWwgb3BlbmlkIHByb2ZpbGUgVXNlci5SZWFkIFVzZXIuUmVhZC5BbGwgVXNlci5SZWFkQmFzaWMuQWxsIiwic2lnbmluX3N0YXRlIjpbImlua25vd25udHdrIiwia21zaSJdLCJzdWIiOiI2SFhKb0tXYVNQTGdLNWZocTVQdFZjX0ItbF8wcmxqT2JTaXlHSzVxTm5FIiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IkVVIiwidGlkIjoiM2FhNGEyMzUtYjZlMi00OGQ1LTkxOTUtN2ZjZjA1YjQ1OWIwIiwidW5pcXVlX25hbWUiOiJTS0hBTUBlcXVpbm9yLmNvbSIsInVwbiI6IlNLSEFNQGVxdWlub3IuY29tIiwidXRpIjoiRVJJZXIwYU5NMG1kYzZzS0xQQUdBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19zdCI6eyJzdWIiOiJwc1N6UGlrdzhFSFVPRlpURkVoVEthZmhhLWZsQ193TDhDbHJaYkJGTnBFIn0sInhtc190Y2R0IjoxMzQ0NTgzNjAyLCJ4bXNfdGRiciI6IkVVIn0.FeiOKWuBMpSYT7TuVod2xKBqlnp0yUQjgNkp6y-xN8PwxZE_40wxciAlqKWJJ95cY9Bw2Mi8fVhdLTtNvn6nDYeUNFoQvM8B0OKrKFaUvm2wb-_PuDg3EX07McphgBH9F_2T37A8DkegLweinWpDTi8jHlwqkfDRdIWwGHsPN4l8_hyVFBEKDRfPaqr9QmlhURxTvpVU40gh2kDrZt92u1izbfDNL_INwU3ll8tfSSQETabJW7pqlF173CUFM0FImD7gwfvmBLGZBOxF9zidLRs802An-saO0bD8gYD6KFs-9YFTcYThHl1nydwuzwgOLuPAsGwF_97cglJJIM4JIw'
        else:
            token = flask.request.headers["X-Auth-Request-Access-Token"]

        df_user_projects = SurfaceModel.get_user_project(
            token, server_names_fil)

        return (
            False,
            SurfaceModel.get_server_names(df_user_projects),
        )

# SET SERVER END


# SET PROJECT START

    @callback(
        [
            Output(get_uuid(LayoutElements.PROJECT_DROPDOWN), "value"),
            Output(get_uuid(LayoutElements.PROJECT_DROPDOWN), "options"),
        ],
        [
            Input(get_uuid(LayoutElements.SERVER_DROPDOWN), "value")
        ],
    )
    def _set_projects(
        server_value: str

    ) -> dict:

        if server_value:
            global df_user_projects
            database_names_fil = sever_names.loc[sever_names['sourceProjectId']
                                                 == int(server_value)]['sourceDatabase']

            project_names_fil = sever_names.loc[sever_names['sourceDatabase']
                                                == (database_names_fil.iloc[0])]
            project_names_fil.objectId = project_names_fil.objectId.str.split(
                ',')
            project_names_fil = project_names_fil.explode('objectId')
            df_user_projects = df_user_projects[['objectId']]
            df_res = pd.merge(df_user_projects,
                              project_names_fil, on='objectId')
            return (
                False,
                SurfaceModel.get_project_names(df_res),
            )
        else:
            return (
                False,
                False,
            )


# SET PROJECT END

# SET ISET START


    @callback(
        [
            Output(get_uuid(LayoutElements.ISET_DROPDOWN), "value"),
            Output(get_uuid(LayoutElements.ISET_DROPDOWN), "options"),
            Output(get_uuid(LayoutElements.ISET_DROPDOWN), "disabled"),
        ],
        [
            Input(get_uuid(LayoutElements.PROJECT_DROPDOWN), "value"),
            State(get_uuid(LayoutElements.SOURCE_DB_DROPDOWN), "value")
        ],
    )
    def _set_iset(
        project_value: str, source_db_value: str
    ) -> dict:
        db_name = SurfaceModel.source_db[source_db_value]
        if db_name == 'OW':
            iset_disabled = False
        else:
            iset_disabled = True

        if project_value:
            iset_names_fil = iset_names.loc[iset_names['sourceProjectId']
                                            == int(project_value)]
            return (
                False,
                SurfaceModel.get_iset_names(iset_names_fil),
                iset_disabled

            )
        else:
            return (
                False,
                False,
                iset_disabled

            )
# SET ISET END

# SET GRID START
    @callback(
        [
            Output(get_uuid(LayoutElements.GRID_DROPDOWN), "value"),
            Output(get_uuid(LayoutElements.GRID_DROPDOWN), "options"),
        ],
        [
            Input(get_uuid(LayoutElements.ISET_DROPDOWN), "value"),
            State(get_uuid(LayoutElements.PROJECT_DROPDOWN), "value")
        ],
    )
    def _set_grid(
        iset_value: str,
        project_value: str

    ) -> dict:

        if project_value and iset_value:
            grid_names_fil = grid_names.loc[(grid_names['interpretationSetId'] == int(
                iset_value)) & (grid_names['sourceProjectId'] == int(project_value))]
        elif project_value and (iset_value is False or iset_value is None):
            grid_names_fil = grid_names.loc[(grid_names['interpretationSetId'] == 0) & (
                grid_names['sourceProjectId'] == int(project_value))]
        else:
            return (
                False,
                False,

            )

        return (
            False,
            SurfaceModel.get_grid_names(grid_names_fil),

        )
