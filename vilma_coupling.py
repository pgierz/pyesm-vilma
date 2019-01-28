"""
Allows for coupling between ``ECHAM6`` and a **generic ice sheet**

- - - - 
"""

# Standard Library Imports:
import glob
import logging
import os
import tempfile

# This Library Imports:
from pyesm.component.component_coupling import ComponentCouple
from pyesm.vilma.vilma_simulation import VilmaCompute
from pyesm.helpers import load_environmental_variable_1_0, ComponentFile, FileDict
from pyesm.time_control import CouplingEsmCalendar

# External Imports:
import cdo


class VilmaCouple(VilmaCompute, ComponentCouple):
    """ Contains functionality to cut out ice sheet forcing from ECHAM6 output """
    COMPATIBLE_COUPLE_TYPES = ["ice"]

    def __init__(self, **VilmaComputeArgs):
        super(VilmaCouple, self).__init__(**VilmaComputeArgs)


    def recieve_ice(self):
        """
        Should replace an input file to have the following attributes:

        dimensions:
        epoch = UNLIMITED ; // (97 currently)
        lon = 512 ;
        lat = 256 ;
        variables:
        double epoch(epoch) ;
        epoch:calendar = "proleptic_gregorian" ;
        epoch:standard_name = "time" ;
        epoch:units = "ka BP" ;
        epoch:long_name = "Epoch" ;
        double lon(lon) ;
        lon:standard_name = "longitude" ;
        lon:long_name = "longitude" ;
        lon:units = "degrees_east" ;
        lon:axis = "X" ;
        double lat(lat) ;
        lat:standard_name = "latitude" ;
        lat:long_name = "latitude" ;
        lat:units = "degrees_north" ;
        lat:axis = "Y" ;
        float Ice(epoch, lat, lon) ;
        Ice:long_name = "z" ;
        Ice:grid_type = "gaussian" ;
        Ice:_FillValue = NaNf ;
        Ice:missing_value = NaNf ;
        Ice:actual_range = 0., 3423. ;
        """
        self.CDO.remapcon("n128",
                     input="-setgrid,"+self.files["couple"]["ice_grid"]+" "+self.files["couple"]["ice_file"],
                     options="-P 8 -f nc")

    def send_ice(self):
        """ Sends a generic solid earth field for an ice sheet model """
        self._generate_ice_forcing_file()
        self._write_grid_description()
        self._write_variable_description()
        self.files['couple'].digest()
        for tmpfile in self._cleanup_list:
            os.remove(tmpfile)
        self.CDO.cleanTempDir()

    def _generate_ice_forcing_file(self):
         """ Generates information for a ice sheet
         
         The file rsl contains relative sea level information, but is continueously updated, so we should always cut out the **first** or **last** step
         Question:
         first or last timestep
         """
         ofile = self.CDO.seltimestep("-1", input=self.files["outdata"]["rsl"]._current_location)
         self.files["couple"][self.Type+"_file"] = ComponentFile(src=ofile, dest=self.couple_dir+"/"+self.Type+"_file_for_ice.nc")

    def _write_grid_description(self):
         """ Writes a grid description file of Vilma output """
         grid_des = self.CDO.griddes(input=self.files["couple"][self.Type+"_file"]._current_location)
         with open(self.couple_dir+"/"+self.Type+".griddes", "w") as grid_file:
                 grid_file.write("\n".join(grid_des))

    def _write_variable_description(self):
         """ Writes a file which describes the variables that could be sent to an ice model """
         with open(self.couple_dir+"/"+self.Type+"_variables.dat", "w") as variable_file:
                 # Relative Sea Level
                 variable_file.write("solid_earth_relative_sea_level_variablename=rsl\n")
                 variable_file.write("solid_earth_relative_sea_level_units=m\n")  # relative to 0 in the initial file
                 # Bathymetry
                 variable_file.write("solid_earth_orography_variablename=topo\n")  # in the initial file
                 variable_file.write("solid_earth_orography_units=0\n")  # in the initial file
