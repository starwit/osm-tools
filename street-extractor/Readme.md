# Street Extractor
This component downloads all street segments for a given city. It can then create CSV files with names and line strings as well as SQL imports for PostGIS.

## How to use

Tools consists of two parts, extractor and PostGIS exporter. The first one extracts for a given city all streets and stores output as a gpkg file. PostGIS exporter creats SQL inserts and can import them into a PostGIS instance.

```bash
poetry install
# extractor
poetry run python extractor.py "Wolfsburg, Germany"

# PostGIS exporter
poetry run python postgis_export.py Wolfsburg_Germany_street_segments.gpkg Wolfsburg db_name db_user db_password localhost 5432
```

