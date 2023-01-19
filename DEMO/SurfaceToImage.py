import xtgeo
import requests
import io


surface_stream = requests.get(
    "https://dlssdfsandbox.blob.core.windows.net/dls/SpatialDB/work/POC/rotated/5099.gri?sp=r&st=2022-11-24T14:15:50Z&se=2023-08-30T22:15:50Z&spr=https&sv=2021-06-08&sr=b&sig=tiS7dQcV5b6J5zNW42MdV1PluhUj98Vigt%2FYmHdY%2FrY%3D",
    stream=True,
)
surface = xtgeo.surface_from_file(
    io.BytesIO(surface_stream.content))

surface.quickplot