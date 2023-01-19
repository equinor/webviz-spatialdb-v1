import io
import requests
from flask import send_file
import numpy as np
import xtgeo
import dash
import webviz_subsurface_components as wsc
from dash import dcc, html

def get_surface_float32(surface: xtgeo.RegularSurface) -> io.BytesIO:
    values = surface.values.astype(np.float32)
    values.fill_value = np.NaN
    values = np.ma.filled(values)

    # Rotate 90 deg left.
    # This will cause the width of to run along the X axis
    # and height of along Y axis (starting from bottom.)
    values = np.rot90(values)

    byte_io = io.BytesIO()
    byte_io.write(values.tobytes())
    byte_io.seek(0)
    return byte_io


img_url = "https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/work/5099.png?sp=r&st=2022-12-12T13:17:22Z&se=2023-08-29T21:17:22Z&spr=https&sv=2021-06-08&sr=b&sig=VNCOmTpb886a9i0PRIEkTxcYtwdG8%2FejCbsjuY9RO%2FM%3D"


url_5099="https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/work/POC/5099.gri?sp=r&st=2022-12-21T13:35:13Z&se=2025-12-21T21:35:13Z&spr=https&sv=2021-06-08&sr=b&sig=MmxlRAmrRtsp42ZjzgvY%2BJa5TjRBYYd0mrHd%2Fr%2Bd%2FdM%3D"
surface_stream = requests.get(
    # "https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/work/POC/rotated/5099.gri?sp=r&st=2022-11-24T14:15:50Z&se=2023-08-30T22:15:50Z&spr=https&sv=2021-06-08&sr=b&sig=tiS7dQcV5b6J5zNW42MdV1PluhUj98Vigt%2FYmHdY%2FrY%3D",
    url_5099,
    stream=True,
)

depth_surface = xtgeo.surface_from_file(io.BytesIO(surface_stream.content))
print(depth_surface)

app = dash.Dash(__name__)

app.layout = wsc.DeckGLMap(
    id="deckgl-map",

    layers=[
        {
            "@@type": "AxesLayer",
            "id": "axes-layer",
            "bounds": [
                depth_surface.xmin,
                depth_surface.ymin,
                -np.nanmax(depth_surface.values),
                depth_surface.xmax,
                depth_surface.ymax,
                np.nanmin(depth_surface.values),
            ],
        },

        {
            "@@type": "MapLayer",
            "id": "mesh-layer2",
            "meshUrl": "/map/mesh",
            "frame": {
                "origin": [depth_surface.xori, depth_surface.yori],
                "count": [depth_surface.ncol, depth_surface.nrow],
                "increment": [depth_surface.xinc, depth_surface.yinc],
                "rotDeg": depth_surface.rotation,
            },
            "contours": [0, 100],
            "isContoursDepth": True,
            "gridLines": False,
            "material": True,
            "name": "mesh",
        },
    ],
    views={
        "layout": [1, 2],
        "showLabel": True,
        "viewports": [
            {
                "id": "view_2",
                "show3D": False,
                "name": "Depth surface",
                "layerIds": [ "mesh-layer2"],
                "isSync": False,
            },
        ],
    },
)


@app.server.route("/map/<map_name>")
def send_map(map_name: str):
    return send_file(
        get_surface_float32(depth_surface), mimetype="application/octet-stream"
    )


if __name__ == "__main__":
    app.run_server()
