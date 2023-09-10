# Sigma_SLF_Pythonscripts
SLF files from Sigma bicycle computers are XML-Files with proprietary specification.

As the file structure is different for the bicycle computer generations, not all SLF-imports can handle all SLF-files.

I use GoldenCheetah with Strava and when exporting the Sigma-data as FIT-file, Strava always saved the height data, until 2023. 
In 2023 height data was not saved anymore by Strava without GPX-data, so I had to combine my SLF-data with GPX-data. 

Combining data with real time to Sigma-data from non-GPS-computers is not possible, because the SLF-files record only the training data, not the real time. 
Pause times will be saved as markers, but are not included in the time.

I created a script to modify the time to real time.

Maybe there will come further scripts. Feel free to contribute.
