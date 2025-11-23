from requests import Request
from owslib.wfs import WebFeatureService
import geopandas as gpd
import pandas as pd

city = "Wolfsburg"
url = "https://geoportal.stadt.wolfsburg.de/geoserver/opendata_stadtteile/wfs"

wfs = WebFeatureService(url=url)
layers = list(wfs.contents)

def fetch_features(layer_name, fetch_cnt: int, ix: int) -> gpd.GeoDataFrame:
    """Fetch features and return as GeoDataFrame"""
    params = dict(service='WFS', version="2.0.0", request='GetFeature',
        typeName=layer_name, count=fetch_cnt, startIndex=ix*fetch_cnt)
    
    # Parse the URL with parameters
    wfs_request_url = Request('GET', url, params=params).prepare().url
    
    print(wfs_request_url)

    try:
        gdf = gpd.read_file(wfs_request_url, format='GML')
    except ValueError:
        print("Can't read data")
        return
    gdf = gdf.set_crs(epsg=25832)
    gdf = gdf.to_crs(epsg=4326)
    return gdf

def loop_layer(
        layer_name, max_loops: int = 100, item_fetch_cnt: int = 1000) -> gpd.GeoDataFrame:
    """Specify the parameters for fetching the data
    max_loops: how many iterations per layer max
    item_fetch_cnt: specificies amount of rows to return per iteration 
        (e.g. 10000 or 100); check capabilities in browser first
    startIndex: specifies at which offset to start returning rows
    """
    df = None
    cnt = 0
    for ix in range(100):
        df_new = fetch_features(layer_name, item_fetch_cnt, ix)
        if df_new is None:
            print("Empty received, aborting..")
            break
        new_cnt = len(df_new)
        if new_cnt == 0:
            # empty result
            # all rows fetched?
            break
        cnt += new_cnt
        print (f"Round {ix}, retrieved {cnt} features", end="\r")
        if df is None:
            df = df_new
        else:
            df = gpd.concat([df, df_new])
        if new_cnt < item_fetch_cnt:
            break
    return df

def create_sql_inserts(gdf):
    result_query = []
    sql = "INSERT INTO city_district (city, name, gmlid, district_government, district_geometry) VALUES ('{city_name}', '{name}', '{gmlid}', '{district_government}', ST_SetSRID(ST_GeomFromText('{geometry}'),4326));"
    
    for district in gdf.itertuples():
        gmlid = district.id
        name = district.name
        district_government = district.ortsrat
        district_geometry  = district.geometry
    
        #print(sql.format(city_name=city, name=name, gmlid=gmlid, district_government=district_government, geometry=district_geometry))
        result_query.append(sql.format(city_name=city, name=name, gmlid=gmlid, district_government=district_government, geometry=district_geometry))

    return result_query    

def write_sql_to_file(sql, city_name):
    with open(f"{city_name}_insert.sql", 'w') as f:
        f.write("\n".join(sql))

def main():    
    df = loop_layer("opendata_stadtteile:stadtteile")
    sql = create_sql_inserts(df)
    write_sql_to_file(sql, "Wolfsburg")

if __name__ == '__main__':
    main()