#!/bin/env python3

# This script will convert the time of Sigma SLF files to include the pause times given by the Marker-Elements in the XML.
#   This is usefull when combining the SLF file with any other recording (e.g. a gpx file)
#   Please note: There are different SLF-file formats and not all formats do use Marker-Elements for pause. 
#     So this script does not fit to all SLF files. It is tested with an BC23.16 and Sigma Datacenter 5.9.1   
#
# For combining the Sigma-Data with a GPS-recording I do use GoldenCheetah. You have to follow these steps to get a correct combined training recording:
#   - Export your SLF-File from Sigma Datacenter
#   - Correct the SLF-File with this script
#   - Load the SLF File to GoldenCheetah
#   - Apply the GoldenCheetah-tool for correcting gaps to the slf-activity
#   - Correct the start time: If time on your bicycle computer is not set correctly, adapt the start time of the workout in GoldenCheetah to correct time
#   - Load the GPX-File to GoldenCheetah
#   - Apply the GoldenCheetah-tool for correcting gaps to the GPS-activity
#   - Apply the GoldenCheetah-tool for correcting GPS-errors to the gps-activity without any B-Spline correction. (This will correct possible 0-values)
#   - Save _both_ activities
#   - Use GoldenCheetah-Tool to combine activities on the slf-activity; use existing activity, choose the gps-activity, use starting time for sync, and do not change the offset
#

import argparse
import xml.etree.ElementTree as ET

# Commandline arguments
parser = argparse.ArgumentParser(description='Converts the time in a Sigma SLF file from training time only to complete time including pausing time.')
parser.add_argument('Infile', help='SLF-File to convert')
parser.add_argument('Outfile', help='Name of Outputfile', nargs='?', default='out.slf')

args = parser.parse_args()

print(args.Infile, args.Outfile)

# Parsing of input-XML
try:
  slfdata = ET.parse(args.Infile)
except FileNotFoundError:
  print('Given input-file not found')
except ET.ParseError:
  print('Invalid input file given')

# Finding all necessary elements of XML
slfroot = slfdata.getroot()
slfentries = slfroot.find('Entries')
slfmarkers = slfroot.find('Markers')

# Inserting a new attribute for real time
#  we have to keep training time until end of processing, as marker time refers to it
for entry in slfentries:
   entry.set('iRealtime',int(entry.attrib.get('trainingTimeAbsolute')))

# Calculating real time from pause-markers (type = p)
markerindex=0

# Loop for markers
for marker in slfmarkers:
  if marker.attrib.get('type') == 'p':
    markerindex=markerindex+1
    imarkerTime=int(marker.attrib.get('timeAbsolute'))
    imarkerPause=int(marker.attrib.get('duration'))
    firstentry=0
    entryindex=0
# Loop over entries for each marker
    for entry in slfentries:
      trainingtimeabsolute = int(entry.attrib.get('trainingTimeAbsolute'))

# All entries after pause will be shifted
      if trainingtimeabsolute > imarkerTime:
        trainingtime = int(entry.attrib.get('trainingTime'))
        irealtimemoved = entry.attrib.get('iRealtime') + imarkerPause
        entry.set('iRealtime',irealtimemoved)

        # We need an additional entry for the end of the pause, as the SLF-file contains only an entry for the start and the next riding-entry
        #  if we leave this out, an interpolation of data like in GoldenCheetah will lead to increasing recording values e.g. for speed during pause
        if (firstentry == 0):
          # Some of the values of the Entry will be taken from the next entry, because they will change even during pause
          altitude=entry.attrib.get('altitude')
          calories=entry.attrib.get('calories')
          heartrate=entry.attrib.get('heartrate')
          temperature=entry.attrib.get('temperature')
          trainingTimeAbsolute=str(trainingtimeabsolute - trainingtime)
          irealtimenew=irealtimemoved - trainingtime 
          # distanceAbsolute will be taken from previous element (see below)
          # the rest will be set to 0
          newentry = ET.Element('Entry',altitude= altitude ,
              altitudeDifferencesDownhill= '0', altitudeDifferencesUphill= '0', cadence= '0', calories= calories, distance= '0', distanceAbsolute= distanceAbsolute,
              distanceDownhill= '0', distanceUphill= '0', heartrate= heartrate, incline= '0', power= '0', speed= '0', temperature= temperature, trainingTime= '0', 
              trainingTimeAbsolute= trainingTimeAbsolute, powerZone= '1', isActive= '0', timeBelowIntensityZones= '0', timeInIntensityZone1= '0', timeInIntensityZone2= '0', 
              timeInIntensityZone3= '0', timeInIntensityZone4= '0', timeAboveIntensityZones= '0', timeBelowTargetZone= '0', timeInTargetZone= '0', timeAboveTargetZone= '0', 
              useForChart= '0', useForTrack= '1', speedTime= '0', iRealtime = irealtimenew)
          # We must not insert the point at this moment! Otherwise the set of entries will be modified, which we are currently looping over.
          #     Result would be, that the current entry is shifted to next entry and will be treated again in the loop.
          newindex=entryindex
          print('Insert',markerindex,distanceAbsolute)
          
          firstentry=1

      # We do save the distance, because distance for pause-end should be taken from pause-start and not from next riding point
      distanceAbsolute=entry.attrib.get('distanceAbsolute')
      entryindex=entryindex+1

    # Loop over entries has finished, we can now save the additional pause-end-marker
    #   But there is a Pause-Marker at the end, where no firstentry will be found, so no newentry will be created. 
    #    If we don't handle this marker specially, last newentry will be saved twice.
    #    Best way would be to drop this pause, because it is the pause until next reset of data and this could be very long
    if firstentry != 0:
      slfentries.insert(newindex,newentry)
    else:
      print('No firstentry',markerindex)

# Now we are ready and can move realtime to trainingTimeAbsolute
for entry in slfentries:
  entry.set('trainingTimeAbsolute',str(entry.attrib.get('iRealtime')))
  del entry.attrib['iRealtime']
  
# Save, ready
try:
  slfdata.write(args.Outfile)
except:
  print('Error writing output File')



