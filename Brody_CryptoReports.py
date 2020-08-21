# -*- coding: utf-8 -*-
"""
Created on Sat May  9 00:09:32 2020

@author: leo
"""

import papermill as pm


parameters_list=[('minute', './minute_data/Brody_minutes_exe.ipynb','./minute_data/Brody_minutes_exe.html'),
               ('hour', './hour_data/Brody_hours_exe.ipynb','./hour_data/Brody_hours_exe.html'),
               ('day', './day_data/Brody_days_exe.ipynb','./day_data/Brody_days_exe.html')]

for datetime, nb_executed, up_filename in parameters_list:
    pm.execute_notebook(
    './Brody_cryptosMHD.ipynb',
    nb_executed,
    parameters = dict(datetime_interval=datetime, upload_filename=up_filename),
    nest_asyncio=True)
