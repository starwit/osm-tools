import argparse
import pandas as pd
import geopandas as gpd
from shapely import line_merge
from shapely.ops import unary_union, linemerge
from shapely.geometry import MultiLineString
import psycopg2


def generate_postgis_import(gdf, city_name):
    result_query = []
    sql = "INSERT INTO street_catalog (city, street_name, street_path) VALUES ('{city_name}', '{street_name}', ST_SetSRID(ST_GeomFromText('{geometry}'),4326));"
    
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
            result_query.append(sql.format(city_name=city_name, street_name=street_name, geometry=merged.wkt))
        except:
            #print("failed to merge " + street_name)
            geoSeries = gpd.GeoSeries(segments, crs="EPSG:4326")
            multi = MultiLineString([geom for geom in geoSeries if geom is not None])
            result_query.append(sql.format(city_name=city_name, street_name=street_name, geometry=multi.wkt))
            continue

    return result_query
    
def write_sql_to_file(sql, city_name):
    with open(f"{city_name}_insert.sql", 'w') as f:
        f.write("\n".join(sql))

  
def write_to_database(sql):
    conn_params = {
        "dbname": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
        "host": args.db_host,
        "port": args.db_port
    }
    conn = psycopg2.connect(**conn_params)
    for query in sql:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    pass
    
def test_data_from_file():
    gdf = gpd.read_file("Wolfsburg_Germany_street_segments.gpkg")
    sql = generate_postgis_import(gdf, "Wolfsburg")
    write_sql_to_file(sql, "Wolfsburg")
    write_to_database(sql)
    return gdf

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('data_file', help='name of city e.g. Berlin, Germany')
    arg_parser.add_argument('city', help='name of city e.g. Berlin, Germany')
    arg_parser.add_argument('-s', '--sql', help='store generated sql inserts as file')
    arg_parser.add_argument('db_name', help='postgres database name')
    arg_parser.add_argument('db_user', help='postgres user name')
    arg_parser.add_argument('db_password', help='postgres password')
    arg_parser.add_argument('db_host', help='postgres host')
    arg_parser.add_argument('db_port', help='postgres port')
    global args
    args = arg_parser.parse_args() 
    test_data_from_file()
    

if __name__ == '__main__':
    main()