from typing import Callable,  Any, Dict, List
from enum import Enum, unique
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

    MAPHEIGHT = "80vh"
    SIDEBAR = {"flex": 1, "height": "90vh", "overflow-x": "auto"}
    MAINVIEW = {"flex": 3, "height": "90vh"}
    DISABLED = {"opacity": 0.5, "pointerEvents": "none"}
    RESET_BUTTON = {
        "marginTop": "5px",
        "width": "100%",
        "height": "20px",
        "line-height": "20px",
        "background-color": "#7393B3",
        "color": "#fff",
    }
    OPTIONS_BUTTON = {
        "marginBottom": "10px",
        "width": "100%",
        "height": "30px",
        "line-height": "30px",
        "background-color": "lightgrey",
    }


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
    BITMAP_LAYER = "deckglmap3dlayer"
    LAYER_TYPE = "BitmapLayer"
    HILLSHADING_LAYER = "deckglhillshadinglayer"
    FAULTPOLYGONS_LAYER = "deckglfaultpolygonslayer"
    WELLS_LAYER = "deckglwelllayer"


def main_layout(field_uuid: Callable, iset_uuid: Callable, grid_uuid: Callable, graph_uuid: Callable, color_tables: List[Dict],) -> wcc.FlexBox:
    return wcc.FlexBox(
        children=[
            wcc.Frame(
                style={"flex": 1},
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
                                # options=[
                                #     {"label": v, "value": v}
                                #     for k, v in sever_names.items()
                                # ],
                                # value=list(sever_names.values())[0],
                            ),
                            wcc.Dropdown(
                                label="Select Project",
                                id=field_uuid(
                                    LayoutElements.PROJECT_DROPDOWN
                                ),
                            ),
                            wcc.Dropdown(
                                label="Select Interpretation Set",

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
                                label="Quick Load :- ",
                                id=field_uuid(LayoutElements.QUICKLOAD_OPTION),
                                options=[
                                    {"label": "ON", "value": "1"},
                                    {"label": "OFF", "value": "0"}
                                ],
                                vertical=False,
                                value="1",
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
            ),
            wcc.Frame(
                highlight=False,
                style={
                    "height": "800px",
                    "flex": 3,
                },
                children=MapViewLayout(graph_uuid, color_tables=color_tables)
            ),
        ],
    )


class MapViewLayout(FullScreen):
    """Layout for the main view containing the map"""

    def __init__(self, get_uuid: Callable, color_tables: List[Dict]) -> None:
        super().__init__(
            children=html.Div(
                wsc.DeckGLMap(
                    id=get_uuid(LayoutElements.DECKGLMAP),
                    coords={"visible": True,
                            "multiPicking": True, "pickDepth": 10},
                    scale={"visible": True},
                    colorTables=color_tables,
                    bounds=[0, 0, 1000, 1000],
                    layers=[
                        {
                            "@@type": LayoutElements.LAYER_TYPE,
                            "id": LayoutElements.BITMAP_LAYER,
                        },
                    ],
                    coordinateUnit="m",
                ),
                style={"height": LayoutStyle.MAPHEIGHT},
            ),
        )
