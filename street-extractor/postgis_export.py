import pandas as pd
import geopandas as gpd
from shapely import line_merge
from shapely.ops import unary_union, linemerge
import psycopg2


def generate_postgis_import(gdf, city_name):
    result_query = ""
    sql = """
        INSERT INTO streets_catalog (city, street_name, street_path)
        VALUES ('{city_name}', '{street_name}', ST_GeomFromText({geometry}, 4326))
    """
    
    street_names = gdf['street_name'].unique()
    
    for street_name in street_names:
        sample = gdf[gdf['street_name'] == street_name]
        segments = [geom for geom in sample.geometry if geom is not None]
        unioned = unary_union(segments)
        try:
            if len(segments) == 1:
                merged = segments[0]
                continue
            merged = linemerge(unioned)
            #print(segments)
        except:
            print("failed to merge " + street_name)
            print(segments)
            continue
        #print(sql.format(city_name=city_name, street_name=street_name, geometry=merged.wkt))

    
    return result_query
    
    
    
def write_to_database(gdf, city_name, conn_params):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    pass
    
def test_data_from_file():
    gdf = gpd.read_file("Wolfsburg_Germany_street_segments.gpkg")
    generate_postgis_import(gdf, "Wolfsburg")
    return gdf

if __name__ == '__main__':
    test_data_from_file()