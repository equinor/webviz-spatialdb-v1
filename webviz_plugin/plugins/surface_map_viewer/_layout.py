from typing import Callable,  Any, Dict, List
import webviz_core_components as wcc
import webviz_subsurface_components as wsc
from dash import html
from ._business_logic import SurfaceModel

######################################################################
#
# Collection of Dash layout and ID-ownership
#
# Defines the Dash layout, and builds the HTML-element structure
# for the plugin.
#
# Ownership of the layout element ID's, which is provied to the
# various callback Inputs, States and Outputs.
#
######################################################################

# pylint: disable = too-few-public-methods


class LayoutStyle:
    """CSS styling"""

    MAPHEIGHT = "87vh"
    SIDEBAR = {"flex": 1, "width": "100px",
               "height": "90vh", "overflow-x": "auto"}
    MAINVIEW = {"flex": 3, "height": "90vh"}


class FullScreen(wcc.WebvizPluginPlaceholder):
    def __init__(self, children: List[Any]) -> None:
        super().__init__(buttons=["expand"], children=children)


class LayoutElements:
    """
    Definition of names/ID's of HTML-elements in view

    Layout file is owner of ID's and provides the definition to the users,
    e.g. callbacks (Input, State and Output properties).

    NOTE: Other solutions can be used, the main goal is to have a set of defined
    names for element ID which is provided to callbacks - preventing hard coded
    string values.
    """

    DECKGLMAP = "map_viewer"
    SOURCE_DB_DROPDOWN = "sourcedb"
    SERVER_DROPDOWN = "serverdropdown"
    PROJECT_DROPDOWN = "projectdropdown"
    ISET_DROPDOWN = "isetdropdown"
    GRID_DROPDOWN = "griddropdown"
    COLOURMAP_DROPDOWN = "colourmapdropdown"
    QUICKLOAD_OPTION = "quickloadoption"

    COLOUR_SCALE = "COLOUR_SCALE"
    COLORMAP_LAYER = "deckglcolormaplayer"
    BITMAP_LAYER = "deckglbitmapLayer"
    BITMAP_LAYER_TYPE = "BitmapLayer"

    HILLSHADING_LAYER = "deckglhillshadinglayer"
    FAULTPOLYGONS_LAYER = "deckglfaultpolygonslayer"
    WELLS_LAYER = "deckglwelllayer"

    AXES_LAYER = "deckglaxeslayer"
    AXES_LAYER_TYPE = "AxesLayer"
    MAP_LAYER = "deckglmaplayer"
    MAP_LAYER_TYPE = "BitmapLayer"


def main_layout(field_uuid: Callable, iset_uuid: Callable, grid_uuid: Callable, graph_uuid: Callable, color_tables: List[Dict],) -> wcc.FlexBox:
    return wcc.FlexBox(
        children=[
            wcc.Frame(
                children=[
                    wcc.Selectors(
                        label="Source Database",
                        children=[
                            wcc.Dropdown(
                                label="Select Source Database",
                                id=field_uuid(
                                    LayoutElements.SOURCE_DB_DROPDOWN
                                ),
                                options=[
                                    {"label": v, "value": k}
                                    for k, v in SurfaceModel.source_db.items()
                                ],
                                value=list(SurfaceModel.source_db.keys())[0],
                            )
                        ],
                    ),
                    wcc.Selectors(
                        label="Source Parameters",
                        children=[
                            wcc.Dropdown(
                                label="Select Server",
                                id=field_uuid(
                                    LayoutElements.SERVER_DROPDOWN
                                ),
                            ),
                            wcc.Dropdown(
                                label="Select Project",
                                id=field_uuid(
                                    LayoutElements.PROJECT_DROPDOWN
                                ),
                            ),
                            wcc.Dropdown(
                                label="Select Interpretation Set (Optional)",
                                id=iset_uuid(
                                    LayoutElements.ISET_DROPDOWN
                                ),
                            ),

                        ],
                    ),
                    wcc.Selectors(
                        label="Output",
                        children=[
                            wcc.Dropdown(
                                label="Surface Grids",
                                optionHeight=65,
                                id=grid_uuid(
                                    LayoutElements.GRID_DROPDOWN
                                ),
                            )
                        ],
                    ),
                    wcc.Selectors(
                        label="Settings",
                        children=[
                            wcc.RadioItems(
                                label="Quick Load (static image only) :- ",
                                id=field_uuid(LayoutElements.QUICKLOAD_OPTION),
                                options=[
                                    {"label": "ON", "value": "1"},
                                    {"label": "OFF", "value": "0"}
                                ],
                                vertical=False,
                                value="0",
                            ),
                            wcc.Dropdown(
                                label="Select ColourMap",
                                id=field_uuid(
                                    LayoutElements.COLOURMAP_DROPDOWN
                                ),
                                options=[
                                    {"label": v, "value": k}
                                    for k, v in SurfaceModel.COLORMAP_OPTIONS.items()
                                ],
                                value=list(
                                    SurfaceModel.COLORMAP_OPTIONS.keys())[0],
                            )
                        ]
                    ),
                ],
                style={"width": "50px"}
            ),
            wcc.Frame(
                children=[
                    html.Div([
                        wsc.DashSubsurfaceViewer(
                            coords={"visible": True},
                            scale={"visible": True},
                            id=graph_uuid(LayoutElements.DECKGLMAP)
                        ),
                    ],
                        style={
                        "height": "400px",
                        "position": "relative",
                    },
                    ),
                ],
                id='divdeck',
                style={'display': 'block',  "flex": "2"}
            ),
            wcc.Frame(
                children=[
                    html.Div([
                        html.Img(id='image', width='100%'),
                    ],
                    ),
                ],
                id='divimg',
                style={'display': 'none',  "flex": "2"}
            ),
        ],
    )
