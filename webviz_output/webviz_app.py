#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTOMATICALLY MADE FILE. DO NOT EDIT.
# This file was generated by skham on 2023-02-16 with Python executable
# c:\appl\surajit\project\webviz-spdb-v1\webviz-spatialdb\spdb-venv\scripts\python.exe

import logging
import logging.config
import os
import threading
import datetime
from pathlib import Path

from uuid import uuid4

from dash import html, dcc, Dash, Input, Output, callback, callback_context
import webviz_core_components as wcc
from flask_talisman import Talisman
import webviz_config
import webviz_config.plugins
from webviz_config.themes import installed_themes
from webviz_config.common_cache import CACHE
from webviz_config.webviz_store import WEBVIZ_STORAGE
from webviz_config.webviz_assets import WEBVIZ_ASSETS
from webviz_config.webviz_instance_info import WebvizRunMode, WEBVIZ_INSTANCE_INFO
from webviz_config.webviz_factory_registry import WEBVIZ_FACTORY_REGISTRY
from webviz_config.utils import deprecate_webviz_settings_attribute_in_dash_app

import webviz_core_components as wcc


# Start out by setting a sensible configuration for the root logger and setting a global
# loglevel. The (global) loglevel defaults to WARNING, but can be set by the user via
# the --loglevel argument. The call to basicConfig() should happen before any other logging
# related calls, see https://docs.python.org/3/library/logging.html#logging.basicConfig
logging.basicConfig(level=logging.WARNING)

theme = webviz_config.WebvizConfigTheme("equinor")
theme.from_json((Path(__file__).resolve().parent / "theme_settings.json").read_text())
theme.plotly_theme_layout_update({})

app = Dash(
    name=__name__,
    external_stylesheets=theme.external_stylesheets,
    assets_folder=Path("resources") / "assets",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

# For signing session cookies
# Use user provided environment variable if exists, otherwise generate fresh
app.server.secret_key = os.environ.get("WEBVIZ_SESSION_SECRET_KEY") or webviz_config.LocalhostToken.generate_token()

server = app.server

app.title = "SpatialDB Surface Viewer"
app.config.suppress_callback_exceptions = True

# Dash is very eager to configure its own logger by both adding a handler and hardcoding
# the loglevel to INFO. Below we counteract both of these.
# We do not want to show INFO regarding werkzeug routing as that is too verbose.
app.logger.setLevel(logging.WARNING)
app.logger.handlers.clear()
logging.getLogger("werkzeug").setLevel(logging.WARNING)




# Trigger import of plugins used, such that SHARED_SETTINGS_SUBSCRIPTIONS
# is populated before setting webviz_settings



webviz_config.plugins.SurfaceMapViewer




# Create the common webviz_setting object that will get passed as an
# argument to all plugins that request it.
webviz_settings: webviz_config.WebvizSettings = webviz_config.WebvizSettings(
    shared_settings=webviz_config.SHARED_SETTINGS_SUBSCRIPTIONS.transformed_settings(
        {}, Path(__file__).resolve().parent / "examples", True 
    ),
    theme=theme,
)

# Previously, webviz_settings was piggybacked onto the Dash application object.
# For a period of time, keep it but mark access to the webviz_settings attribute
# on the Dash application object as deprecated.
deprecate_webviz_settings_attribute_in_dash_app()
app._deprecated_webviz_settings = {
    "shared_settings" : webviz_settings.shared_settings,
    "theme" : webviz_settings.theme,
    "portable" : True,
}

CACHE.init_app(server)

storage_folder = Path(__file__).resolve().parent / "resources" / "webviz_storage"

WEBVIZ_STORAGE.use_storage = True
WEBVIZ_STORAGE.storage_folder = storage_folder

WEBVIZ_ASSETS.portable = True

run_mode = WebvizRunMode.PORTABLE if True else WebvizRunMode.NON_PORTABLE
WEBVIZ_INSTANCE_INFO.initialize(
    dash_app=app,
    run_mode=run_mode,
    theme=theme,
    storage_folder=storage_folder
)

WEBVIZ_FACTORY_REGISTRY.initialize(None)

use_oauth2 = False

if False and not webviz_config.is_reload_process():
    # When Dash/Flask is started on localhost with hot module reload activated,
    # we do not want the main process to call expensive component functions in
    # the layout tree, as the layout tree used on initialization will anyway be called
    # from the child/restart/reload process.
    app.layout = html.Div()
else:
    count_text_plugins = 0
    page_plugins = {}
    page_settings = {}
    
    page_plugins["surfacemapviewer"] = []
    page_settings["surfacemapviewer"] = []
    
    plugin = webviz_config.plugins.SurfaceMapViewer(app=app, **{})
    if not use_oauth2:
        use_oauth2 = plugin.oauth2 if hasattr(plugin, "oauth2") else use_oauth2

    page_plugins["surfacemapviewer"].extend(plugin.plugin_layout(contact_person=None, plugin_deprecation_warnings=[], argument_deprecation_warnings=[]))
    page_settings["surfacemapviewer"].extend([settings for settings in plugin.get_all_settings()])

    
    
    
    app.layout = html.Div(
        className="layoutWrapper",
        children=[
            dcc.Location(id='location', refresh=True),
            wcc.WebvizContentManager(
                id="webviz-content-manager",
                children=[
                    wcc.Menu(
                        id="main-menu",
                        showLogo=True,
                        menuBarPosition="left",
                        menuDrawerPosition="left",
                        initiallyPinned=True,
                        initiallyCollapsed=False,
                        navigationItems=[{'type': 'page', 'title': 'SurfaceMapViewerv1', 'href': '/surfacemapviewer', 'icon': None}],
                        
                    ),
                    wcc.WebvizSettingsDrawer(
                        id="settings-drawer",
                        children=[],
                    ),
                    wcc.WebvizPluginsWrapper(
                        id="plugins-wrapper",
                        children=[],
                    )
                ]
            ),
        ]
    )

WEBVIZ_FACTORY_REGISTRY.cleanup_resources_after_plugin_init()

theme.adjust_csp({"script-src": app.csp_hashes()}, append=True)
Talisman(server, content_security_policy=theme.csp, feature_policy=theme.feature_policy, force_https=False, session_cookie_secure=False)

oauth2 = webviz_config.Oauth2(app.server) if use_oauth2 else None

@callback(
    Output("plugins-wrapper", "children"),
    Output("settings-drawer", "children"),
    Input("location", "pathname")
)
def update_page(pathname):
    ctx = callback_context
    if ctx.triggered:
        if pathname is not None:
            pathname = pathname.replace("/", "")
        else:
            pathname = ""
    if not pathname:
        pathname = next(iter(page_plugins))
    return page_plugins.get(pathname, ["Oooppss... Page not found."]), page_settings.get(pathname, [])



if __name__ == "__main__":
    # This part is ignored when the webviz app is started
    # using Docker container and uwsgi (e.g. when hosted on Azure).
    #
    # It is used only when directly running this script with Python,
    # which will then initialize a localhost server.

    port = webviz_config.utils.get_available_port(preferred_port=5000)

    token = webviz_config.LocalhostToken(app.server, port, oauth2).one_time_token
    webviz_config.utils.LocalhostOpenBrowser(port, token)

    webviz_config.utils.silence_flask_startup()

    app.run_server(
        host="localhost",
        port=port,
        debug=False,
        use_reloader=False,
        dev_tools_prune_errors=False
        
    )
else:
    # This will be applied if not running on localhost
    if use_oauth2:
        oauth2.set_oauth2_before_request_decorator()