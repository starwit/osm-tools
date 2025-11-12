import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union, linemerge
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np

def load_data_from_osm(place):
    G = ox.graph.graph_from_place(place, network_type="drive")
    edges = ox.graph_to_gdfs(G, nodes=False, edges =  True, fill_edge_geometry=True).to_crs(crs = 23030)
    # for empty streets, check if a ref name is provided (like K90) and use it for name
    edges['name']= np.where(edges['name'].isnull(), edges['ref'], edges['name'])
    edges['street_name'] = edges['name']

    edges['street_name'] = edges['street_name'].apply(
        lambda x: '; '.join(x) if isinstance(x, list) else x
    )

    edges_ll = edges.to_crs(epsg=4326)
    return edges_ll

def geom_to_coords_list(geom):
    """Return a flat list of (lon, lat) coordinate tuples for LineString or MultiLineString."""
    if geom is None:
        return []
    if isinstance(geom, LineString):
        return list(geom.coords)
    if isinstance(geom, MultiLineString):
        coords = []
        for part in geom.geoms:
            coords.extend(list(part.coords))
        return coords
    # other geometry types (Point) -> empty
    return []
        
def concantenate_street_segments(df, name):
    sample = df[df['street_name'] == name]
    street_segments = []
    for row in sample.itertuples():
        street_segments.append(loads(row.coords_wkt))
        
    street_complete = gpd.GeoSeries(street_segments, crs="EPSG:4326")
    return street_complete

def concatenate_streets(df):
    street_names = df['street_name'].unique()
    concatenated_streets = {}

    for street_name in street_names:
        concatenated_streets[street_name] = (concantenate_street_segments(df, street_name))

    concatenated_street_segments = []
    for name, gs in concatenated_streets.items():
        if gs.crs is None:
            gs = gs.set_crs("EPSG:4326")
        temp = gpd.GeoDataFrame({'street_name': name, 'geometry': list(gs)})
        concatenated_street_segments.append(temp)
        
    gdf = pd.concat(concatenated_street_segments, ignore_index=True)
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs="EPSG:4326")
    return gdf

def plot_map(gdf):
    fig, ax = plt.subplots(figsize=(10, 10))
    for street_name, group in gdf.groupby('street_name'):
        group.plot(ax=ax, linewidth=0.5)

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.set_axis_off()
    ax.legend()
    ax.set_title("Street segments (one color per street)")
    plt.savefig("streets_map.png", dpi=300, bbox_inches='tight')


place = "Wolfsburg, Germany"

edges_ll = load_data_from_osm(place)

# convert edge data to lat/lon coordinates
df = edges_ll.reset_index().copy()  # keep u, v, key columns
df['coords_list'] = df['geometry'].apply(geom_to_coords_list)
df['coords_wkt']  = df['geometry'].apply(lambda g: g.wkt if g is not None else None)

print(df.head())    

gdf = concatenate_streets(df)

plot_map(gdf)

gdf.to_csv("street_names.csv", index=False)
gdf.to_file("streets_edges.gpkg", layer="streets", driver="GPKG")
