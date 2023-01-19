# Databricks notebook source
import pandas as pd
import numpy as np
import xtgeo


# COMMAND ----------

df=pd.read_csv('C:\Appl\Surajit\Project\webviz-spdb-main\DEMO\GRID.csv')


# COMMAND ----------

dfnew=df.filter(df['gridId']==2657)


# COMMAND ----------

json_dict = dfnew.collect()[0]
ncol, nrow = int(json_dict['NROW']),int(json_dict['NCOL'])
xori, yori = float(json_dict['XORI']), float(json_dict['YORI'])
xinc, yinc = float(json_dict['XINC']), float(json_dict['YINC'])
rotation = float(json_dict['ROTATION'])
ncol, nrow

# COMMAND ----------


# path='dbfs:/mnt/adlsandboxaim/SpatialDB/processed/surface_coordinates/BG4FROST_GULLFAKS/5099/z/part_000.parquet'

# df_z=spark.read.parquet(path)

path='C:\Appl\Surajit\Project\webviz-spdb-main\DEMO\2657.parquet'
pandas_df = pd.read_parquet(path)
  

values = pandas_df['z'].to_numpy(copy=True)
values = np.reshape(values, (nrow,ncol)).astype(np.float32)
values = np.transpose(values)
ncol, nrow, xori, yori, xinc, yinc, rotation,values

# COMMAND ----------

# create xtgeo surface
surf = xtgeo.RegularSurface(ncol=ncol, nrow=nrow,
                            xori=xori, yori=yori,
                            xinc=xinc, yinc=yinc, rotation=rotation,
                            values=values)
surf.quickplot('2657.png')

# COMMAND ----------


