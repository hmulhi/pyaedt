"""
Maxwell 3D: magnet DC analysis
------------------------------
This example shows how you can use PyAEDT to create a Maxwell DC analysis,
compute mass center, and move coordinate systems.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

from pyaedt import Maxwell3d
from pyaedt import generate_unique_project_name
import os
import tempfile

##########################################################
# Set AEDT version
# ~~~~~~~~~~~~~~~~
# Set AEDT version.

aedt_version = "2024.1"

###########################################################################################
# Create temporary directory
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create temporary directory.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. 
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT in graphical mode.

m3d = Maxwell3d(projectname=generate_unique_project_name(),
                specified_version=aedt_version,
                new_desktop_session=True,
                non_graphical=non_graphical)

###############################################################################
# Set up Maxwell solution
# ~~~~~~~~~~~~~~~~~~~~~~~
# Set up the Maxwell solution to DC.

m3d.solution_type = m3d.SOLUTIONS.Maxwell3d.ElectroDCConduction

###############################################################################
# Create magnet
# ~~~~~~~~~~~~~
# Create a magnet.

magnet = m3d.modeler.create_box(origin=[7, 4, 22], sizes=[10, 5, 30], name="Magnet", material="copper")

###############################################################################
# Create setup and assign voltage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the setup and assign a voltage.

m3d.assign_voltage(magnet.faces, 0)
m3d.create_setup()

###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

m3d.plot(show=False, output_file=os.path.join(temp_dir.name, "Image.jpg"), plot_air_objects=True)

###############################################################################
# Solve setup
# ~~~~~~~~~~~
# Solve the setup.

m3d.analyze()

###############################################################################
# Compute mass center
# ~~~~~~~~~~~~~~~~~~~
# Compute mass center using the fields calculator.

m3d.post.ofieldsreporter.EnterScalarFunc("X")
m3d.post.ofieldsreporter.EnterVol(magnet.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_X", "Fields")
m3d.post.ofieldsreporter.EnterScalarFunc("Y")
m3d.post.ofieldsreporter.EnterVol(magnet.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_Y", "Fields")
m3d.post.ofieldsreporter.EnterScalarFunc("Z")
m3d.post.ofieldsreporter.EnterVol(magnet.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_Z", "Fields")
m3d.post.ofieldsreporter.CalcStack("clear")

###############################################################################
# Get mass center
# ~~~~~~~~~~~~~~~
# Get mass center using the fields calculator.

xval = m3d.post.get_scalar_field_value("CM_X")
yval = m3d.post.get_scalar_field_value("CM_Y")
zval = m3d.post.get_scalar_field_value("CM_Z")

###############################################################################
# Create variables
# ~~~~~~~~~~~~~~~~
# Create variables with mass center values.

m3d[magnet.name + "x"] = str(xval * 1e3) + "mm"
m3d[magnet.name + "y"] = str(yval * 1e3) + "mm"
m3d[magnet.name + "z"] = str(zval * 1e3) + "mm"

###############################################################################
# Create coordinate system
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Create a parametric coordinate system.

cs1 = m3d.modeler.create_coordinate_system(
    [magnet.name + "x", magnet.name + "y", magnet.name + "z"], reference_cs="Global", name=magnet.name + "CS"
)

###############################################################################
# Save and close
# ~~~~~~~~~~~~~~
# Save the project and close AEDT.

m3d.save_project()
m3d.release_desktop(close_projects=True, close_desktop=True)
temp_dir.cleanup()
