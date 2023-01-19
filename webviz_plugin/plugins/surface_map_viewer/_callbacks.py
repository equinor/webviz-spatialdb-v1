from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from azure.storage.filedatalake import DataLakeServiceClient
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from dash import ALL, MATCH, Input, Output, State, callback, callback_context, no_update
from ._color_tables import default_color_tables
import xtgeo

from ._business_logic import SurfaceModel
from ._layout import LayoutElements


from ._surface_server import SurfaceServer, QualifiedSurfaceAddress, SimulatedSurfaceAddress
from ._surface_data import DirectoryClient
from azure.storage.filedatalake import (
    AccountSasPermissions,
    ContentSettings,
    DataLakeDirectoryClient,
    DataLakeFileClient,
    DataLakeServiceClient,
    EncryptionScopeOptions,
    FileSasPermissions,
    FileSystemClient,
    FileSystemSasPermissions,
    generate_account_sas,
    generate_file_sas,
    generate_file_system_sas,
    ResourceTypes
)
from datetime import datetime, timedelta


AZURE_ACC_NAME = "dlssdfsandbox"
AZURE_PRIMARY_KEY = "hnbCnarDj4A1lWDMWuZ4xcl94tXGQKWBTfDDG3A8NREAvJwMJBiu7i9nmxxCj4jp191pfK4xF3oRkh6uKFSz5Q=="
AZURE_CONTAINER = "dls"


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


AZURE_ACC_NAME = "dlssdfsandbox"
AZURE_PRIMARY_KEY = "hnbCnarDj4A1lWDMWuZ4xcl94tXGQKWBTfDDG3A8NREAvJwMJBiu7i9nmxxCj4jp191pfK4xF3oRkh6uKFSz5Q=="
AZURE_CONTAINER = "dls"


def generate_sas_token_dl(file_name):

    account_url = "https://{}.dfs.core.windows.net/".format(AZURE_ACC_NAME)

    datalake_service = DataLakeServiceClient(
        account_url=account_url, credential=AZURE_PRIMARY_KEY
    )
    filesystem_client = datalake_service.get_file_system_client(
        AZURE_CONTAINER)
    dir_client = filesystem_client.gene.get_directory_client(
        "SpatialDB/work/POC")
    sas = ""
    sas_url = 'https://'+AZURE_ACC_NAME+'.blob.core.windows.net/' + \
        AZURE_CONTAINER+'/SpatialDB/work/POC/'+file_name+'?'+sas
    return sas_url


def generate_sas_token(file_name):
    sas = generate_blob_sas(account_name=AZURE_ACC_NAME,
                            account_key=AZURE_PRIMARY_KEY,
                            container_name=AZURE_CONTAINER,
                            blob_name=file_name,
                            permission=BlobSasPermissions(read=True),
                            expiry=datetime.utcnow() + timedelta(days=30))

    sas_url = 'https://'+AZURE_ACC_NAME+'.blob.core.windows.net/' + \
        AZURE_CONTAINER+'/SpatialDB/work/POC/'+file_name+'?'+sas
    return sas_url


def plugin_callbacks(get_uuid: Callable, iset_names: pd.DataFrame, sever_names: pd.DataFrame, grid_names: pd.DataFrame, surface_server: SurfaceServer):

    @callback(
        [
            Output(get_uuid(LayoutElements.DECKGLMAP), "layers"),
            Output(get_uuid(LayoutElements.DECKGLMAP), "bounds"),
            Output(get_uuid(LayoutElements.DECKGLMAP), "views"),
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

        map_bounds = [451250, 6778750, 464500, 6793250]
        layersid = [LayoutElements.BITMAP_LAYER]

        if grid_value:
            project = project_options[project_value]
            server = server_options[server_value]
            relatie_path = server+"_" + project + "/"
            token = generate_file_system_sas(
                AZURE_ACC_NAME,
                AZURE_CONTAINER,
                AZURE_PRIMARY_KEY,
                FileSystemSasPermissions(
                    write=True, read=True, delete=True),
                datetime.utcnow() + timedelta(days=30),
            )

            blob_url = 'https://' + AZURE_ACC_NAME + \
                '.blob.core.windows.net/' + AZURE_CONTAINER + '/'

            if quickload_value == '1':
                sas_url = blob_url + 'SpatialDB/processed/surface_coordinates/' + relatie_path + 'images/' + \
                    grid_value+'.png?' + token

                layers.extend([
                    {
                        "id": LayoutElements.BITMAP_LAYER,
                        "@@type": LayoutElements.LAYER_TYPE,
                        "image": sas_url,
                        "bounds": map_bounds

                    },
                ]
                )
            else:
                layersid = [LayoutElements.COLORMAP_LAYER,
                            LayoutElements.HILLSHADING_LAYER]

                grid_data = grid_names.loc[(grid_names['gridId'] == (grid_value)) & (
                    grid_names['sourceProjectId'] == int(project_value))]
                if iset_value:
                    grid_data = grid_data.loc[(
                        grid_data['interpretationSetId'] == int(iset_value))]

                json_dict = grid_data.iloc[0]
                path = blob_url+"SpatialDB/processed/surface_coordinates_Z2/" + \
                    relatie_path + grid_value + ".parquet?" + token
                ncol, nrow = json_dict['NCOL'], json_dict['NROW']
                xori, yori = float(json_dict['XORI']), float(json_dict['YORI'])
                xinc, yinc = float(json_dict['XINC']), float(json_dict['YINC'])
                rotation = float(json_dict['ROTATION'])

                df = pd.read_parquet(path)

                values = df['z'].to_numpy(copy=True)
                values = values*-1
                values = np.reshape(values, (nrow, ncol)).astype(np.float32)
                values = np.transpose(values)

                # ncol, nrow = nrow, ncol  # note flip on ncol/nrow definition
                surface = xtgeo.RegularSurface(ncol=ncol, nrow=nrow,
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
                surface_server.publish_surface(qualified_address, surface)
                url = surface_server.encode_partial_url(qualified_address)
                surf_meta = surface_server.get_surface_metadata(
                    qualified_address)

                colormapname = SurfaceModel.COLORMAP_OPTIONS[colour_value]



                map_bounds = [surf_meta.x_min,
                              surf_meta.y_min,
                              surf_meta.x_max,
                              surf_meta.y_max, ]
                layers.extend([
                    {
                        "id": LayoutElements.COLORMAP_LAYER,
                        "@@type": "ColormapLayer",
                        "visible": True,
                        "colorMapName": colormapname,
                        "valueRange": [surf_meta.val_min, surf_meta.val_max],
                        "image": url,
                        "rotDeg": surf_meta.deckgl_rot_deg,
                        "bounds": surf_meta.deckgl_bounds,

                    },
                    {
                        "id": LayoutElements.HILLSHADING_LAYER,
                        "@@type": "Hillshading2DLayer",
                        "colorMapName": colormapname,
                        "valueRange": [surf_meta.val_min, surf_meta.val_max],
                        "image": url,
                        "visible":True,
                        "rotDeg": surf_meta.deckgl_rot_deg,
                        "bounds": surf_meta.deckgl_bounds,
                    },
                ])

        else:
            layers.extend([
                {
                    "@@type": LayoutElements.LAYER_TYPE,
                    "id": LayoutElements.BITMAP_LAYER,
                    "bounds": map_bounds
                },
            ])

        map_views = {
            "layout": [1, 1],
            "showLabel": False,
            "viewports": [
                {
                    "id": "deck_view",
                    "show3D": False,
                    "layerIds": layersid,
                }
                for view in range(1)
            ],
        }

        return (layers, map_bounds, map_views)

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

        return (
            False,
            SurfaceModel.get_server_names(server_names_fil),

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
            database_names_fil = sever_names.loc[sever_names['sourceProjectId']
                                                 == int(server_value)]['sourceDatabase']

            project_names_fil = sever_names.loc[sever_names['sourceDatabase']
                                                == (database_names_fil.iloc[0])]
            return (
                False,
                SurfaceModel.get_project_names(project_names_fil),

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
        ],
        [
            Input(get_uuid(LayoutElements.PROJECT_DROPDOWN), "value")
        ],
    )
    def _set_iset(
        project_value: str
    ) -> dict:
        if project_value:
            iset_names_fil = iset_names.loc[iset_names['sourceProjectId']
                                            == int(project_value)]
            return (
                False,
                SurfaceModel.get_iset_names(iset_names_fil),

            )
        else:
            return (
                False,
                False,

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
