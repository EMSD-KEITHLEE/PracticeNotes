import pandas as pd
import numpy as np
import os
import csv

from brickschema import Graph, GraphCollection
from brickschema.namespaces import A, BRICK, UNIT, RDF, RDFS, REF
from rdflib import Namespace, Literal, BNode

df = pd.read_csv('./FileName.csv')
BLDG = Namespace("https://www.wsp.com#")

Building = Floor = Room = Equipment = Equipment_name = Point = Site_string = Database = None

## Multiple Building
Site = "Head_Office" #must have no space, can use underscore
Building = df["Building"]
Floor = df["Floor"]
Equipment = df["Equipment_type"]
Equipment_name = df["Equipment_name"]
Point = df["Point_type"]

g = Graph()
g.bind("BLG", BLDG)
g.add((BLDG[Building[0]], A, BRICK.Building))

for index, row in df.iterrows(): 
    # Add Floor and link with Building
    if pd.notnull(row["Floor"]):
        g.add((BLDG[row["Floor"]], A, BRICK.Floor))
        g.add((BLDG[row["Building"]], BRICK.hasPart, BLDG[row["Floor"]]))

    # Add System and link with Building
    if pd.notnull(row["System"]):
        g.add((BLDG[row["System"]], A, BRICK[row["System_SemanticAI"]]))   # Why Brick type = System name?
        g.add((BLDG[row["Building"]], BRICK.hasPart, BLDG[row["System"]]))

    # Add Equipment and link with System
    if pd.notnull(row["Equipment_name"]):
        g.add((BLDG[row["Equipment_name"]], A, BRICK[row["Equipment_SemanticAI"]]))   # Why Brick type = System name?
        g.add((BLDG[row["System"]], BRICK.hasPart, BLDG[row["Equipment_name"]]))

    # Add Point and link with Equipment
    if pd.notnull(row["Point_type"]):
        g.add((BLDG[row["Equipment_point"]], A, BRICK[row["Point_SemanticAI"]]))   # Why Brick type = System name?
        g.add((BLDG[row["Equipment_name"]], BRICK.hasPoint, BLDG[row["Equipment_point"]]))       

    # Add External Reference to Points
    if pd.notnull(row["Database"]):
        # External Ref: Times Series data
        timeserie = BNode()
        DATABASE = Namespace("http://wsp.com/rdcc/db#")
        Database = df["Database"]
        g.bind("database", DATABASE)
        g.add((DATABASE[Database[0]], A, REF.DATABASE))
        g.add((DATABASE[Database[0]], REF.label, Literal("Postgres Timeseries Storage")))
        g.add((DATABASE[Database[0]], REF.connstring, Literal("postgres://1.2.3.4/data")))

        g.add((BLDG[Equipment_name[index]], REF.hasExternalReference, timeserie))
        g.add((timeserie, A, REF.TimeseriesReference))
        g.add((timeserie, REF.hasTimeseriesId, Literal(row["TimeSeriesID"])))
        g.add((timeserie, REF.storedAt, DATABASE[Database[0]]))

if os.path.isfile('./relationship.csv') == True:
    relationship_df = pd.read_csv('./relationship.csv')
    for index, row in relationship_df.iterrows():
        source_asset_code = row["source_asset_code"]
        dest_asset_code = row["dest_asset_code"]
        relationship = row["relationship"]
        g.add((BLDG[source_asset_code], BRICK[relationship], BLDG[dest_asset_code]))

g.serialize("Output.ttl", format="ttl")
print("Export Successful")
