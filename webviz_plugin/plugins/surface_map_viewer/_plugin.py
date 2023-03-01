from typing import Union, Type, List

from webviz_config import WebvizPluginABC

from dash.development.base_component import Component

from ._business_logic import SurfaceModel
from ._callbacks import plugin_callbacks
from ._layout import main_layout

import pandas as pd
from webviz_config.common_cache import CACHE
from webviz_config.webviz_store import webvizstore
from dash import Dash
from .surface_array_server import SurfaceArrayServer
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from ._color_tables import default_color_tables


class SurfaceMapViewer(WebvizPluginABC):
    """
    This Webviz plugin, to illustrate a best practice on code structure and how to
    separate code for clarity and usability.

    The plugin subclasses the abstract WebvizPluginABC base class, and implements
    the required layout function, in addition to callback functionality.

    `Plugin functionality`:
    Plugin contains a model for graph data, which is populated with a set of mocked up
    graph data with unique names. The plugin provides a dropdown for selecting a
    specific graph name from the set and show the graph data in plot. The model provides
    additional ad-hoc calculations (raw, reversed and flipped) for the selected graph
    data. Based on selected visualization option in the layout, the callback retrieves
    correct graph data from the model and provides it to the graph builder in the property
    serialization. Graph type options are provided (line plot and bar chart) as radio items
    for specifying which type of graphing should be used in the graph builder. When the
    graph is built, the builder can provide the JSON serialized result for the callback
    Output.

    `Plugin file structure:`
    * _layout.py - Dash layout and ID-ownership
    * _callbacks.py - Dash callbacks for handling user interaction and update of view
    * _business_logic.py - Query database/input for relevant data and necessary
    ad-hoc calculations for data, separated from Dash specific code (no dash* import)
    * _prop_serialization.py - De-serializing and serializing callback property formats.
    Convert callback Input/State from JSON serializable property formats to strongly typed
    formats (de-serialize) for business logic. Create/build JSON serializable properties
    for Dash callback Output property by use of data from business logic.
    """

    def __init__(self, app: Dash) -> None:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        super().__init__()
        # self.projects_file = projects_file
        # self.isets_file = isets_file
        # self.grids_file = grids_file
        self.projects_file = "https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/processed/webviz_data/projects.json?sp=r&st=2023-01-15T07:15:32Z&se=2025-01-15T15:15:32Z&spr=https&sv=2021-06-08&sr=b&sig=FrOMFhIjC4yEWc3ZRRTFAfZjN%2F%2B6sN%2BdgNKI64QrNRQ%3D"
        self.isets_file = "https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/processed/webviz_data/isets.json?sp=r&st=2023-01-15T07:16:19Z&se=2025-01-15T15:16:19Z&spr=https&sv=2021-06-08&sr=b&sig=af5mXYUB2IA2sbnaPGehGv%2BFQAcTVnlwLZ4%2BhTDTWig%3D"       
        self.grids_file = "https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/processed/webviz_data/grids.json?sp=r&st=2023-01-15T07:11:38Z&se=2025-01-15T15:11:38Z&spr=https&sv=2021-06-08&sr=b&sig=hOcIp%2B4MpPauIeKigTtT4n99F4bSAh3%2B31eVA0%2BJUPc%3D"

        self.projects_df = pd.read_json(self.projects_file)
        self.isets_df = pd.read_json(self.isets_file)
        self.grids_df = pd.read_json(self.grids_file)


        self.grids_df = self.grids_df.fillna(0)
        self.grids_df = self.grids_df.astype({"interpretationSetId": int})

        self._sever_names = SurfaceModel.get_server_names(self.projects_df)
        self._project_names = SurfaceModel.get_project_names(self.projects_df)
        self._iset_names = SurfaceModel.get_iset_names(self.isets_df)
        self._grid_names = SurfaceModel.get_grid_names(self.grids_df)
        self.color_tables = default_color_tables
        self._surface_server = SurfaceArrayServer.instance(app)
        self.set_callbacks()
        load_dotenv()

    def add_webvizstore(self) -> List[tuple]:
        return [(get_data, [{"file_path": self.projects_file}]),
                (get_data, [{"file_path": self.isets_file}]),
                (get_data, [{"file_path": self.grids_file}])]

    @property
    def layout(self) -> Union[str, Type[Component]]:
        return main_layout(
            field_uuid = self.uuid,
            iset_uuid = self.uuid,
            grid_uuid = self.uuid,
            graph_uuid = self.uuid,
            color_tables = self.color_tables
        )

    def set_callbacks(self) -> None:
        plugin_callbacks(self.uuid,
                         iset_names = self.isets_df,
                         sever_names = self.projects_df,
                         grid_names = self.grids_df,
                         surface_server = self._surface_server,
                         )


@CACHE.memoize()
@webvizstore
def get_data(file_path) -> pd.DataFrame:
    return pd.read_json(file_path)
