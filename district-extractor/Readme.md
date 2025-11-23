# District Extractor
This tool shall create PostGIS SQL inserts for city districts. It reads as an example district data from the city of Wolfsburg. Have a look at Wolfsburg's [Geo Portal](https://geoportal.stadt.wolfsburg.de/) for more details.
Downloaded districts are then saved as SQL inserts.


## How to use

Too uses Poetry for dependency management and can be run like so:
```bash
poetry install
poetry run python postgis_export.py
```
After running tool a SQL script is created, that contains all city districts.
