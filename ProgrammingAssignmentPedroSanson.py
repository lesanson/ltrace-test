import ctk
import logging
import qt
import slicer
from slicer.ScriptedLoadableModule import *
import vtk 

import cv2 as cv
import numpy as np
import vtk.util.numpy_support as vtk_np

# Rename "PedroSanson" everywhere in this file to your first and last name. Also rename this file and its folder.
# You'll have to do the widget connections in ProgrammingAssignmentPedroSansonWidget.
# Do your work in the method ProgrammingAssignmentPedroSansonLogic.run.


class ProgrammingAssignmentPedroSanson(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:

    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        applicant_name = "Pedro Sanson"
        self.parent.title = "Programming Assignment: {}".format(applicant_name)
        self.parent.categories = ["Programming Assignment"]
        self.parent.dependencies = []
        self.parent.contributors = [applicant_name]
        self.parent.helpText = ""
        self.parent.acknowledgementText = ""


class ProgrammingAssignmentPedroSansonWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:

    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...

        #
        # Parameters Area
        #
        parameters_collapsible_button = ctk.ctkCollapsibleButton()
        parameters_collapsible_button.text = "Parameters"
        self.layout.addWidget(parameters_collapsible_button)

        # Layout within the dummy collapsible button
        parameters_form_layout = qt.QFormLayout(parameters_collapsible_button)

        #
        # input volume selector
        #
        self.input_selector = slicer.qMRMLNodeComboBox()
        self.input_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.input_selector.selectNodeUponCreation = True
        self.input_selector.addEnabled = False
        self.input_selector.removeEnabled = False
        self.input_selector.noneEnabled = False
        self.input_selector.showHidden = False
        self.input_selector.showChildNodeTypes = False
        self.input_selector.setMRMLScene(slicer.mrmlScene)
        self.input_selector.setToolTip("Pick the input to the algorithm.")
        parameters_form_layout.addRow("Input Volume: ", self.input_selector)

        #
        # output volume selector
        #
        self.output_selector = slicer.qMRMLNodeComboBox()
        self.output_selector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.output_selector.selectNodeUponCreation = True
        self.output_selector.addEnabled = True
        self.output_selector.renameEnabled = True
        self.output_selector.removeEnabled = True
        self.output_selector.noneEnabled = False
        self.output_selector.showHidden = False
        self.output_selector.showChildNodeTypes = False
        self.output_selector.setMRMLScene(slicer.mrmlScene)
        self.output_selector.setToolTip("Pick the output to the algorithm.")
        parameters_form_layout.addRow("Output Volume: ", self.output_selector)

        #
        # threshold value
        #
        self.image_threshold_slider_vidget = ctk.ctkSliderWidget()
        self.image_threshold_slider_vidget.singleStep = 0.01
        self.image_threshold_slider_vidget.minimum = 0
        self.image_threshold_slider_vidget.maximum = 1
        self.image_threshold_slider_vidget.value = 0.5
        parameters_form_layout.addRow("Image threshold", self.image_threshold_slider_vidget)

        #
        # Apply Button
        #
        self.apply_button = qt.QPushButton("Apply")
        self.apply_button.toolTip = "Run the algorithm."
        self.apply_button.enabled = True
        parameters_form_layout.addRow(self.apply_button)
        
        # connections
        self.apply_button.clicked.connect(self.onApplyButtonClick)
        self.logic = ProgrammingAssignmentPedroSansonLogic()

        # Add vertical spacer
        self.layout.addStretch(1)
    
    def onApplyButtonClick(self):
            input_volume = self.input_selector.currentNode()
            output_volume = self.output_selector.currentNode()
            image_threshold = self.image_threshold_slider_vidget.value
            
            if self.logic.run(input_volume, output_volume, image_threshold):
                slicer.util.infoDisplay("Thresholding completed successfully.", windowTitle="Success")
    
    def cleanup(self):
        pass


class ProgrammingAssignmentPedroSansonLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual computation done by your module.

    The interface should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def has_image_data(self, volume_node):
        """This is an example logic method that returns true if the passed in volume node has valid image data"""
        if not volume_node:
            logging.debug("has_image_data failed: no volume node")
            return False
        if volume_node.GetImageData() is None:
            logging.debug("has_image_data failed: no image data in volume node")
            return False
        return True

    def is_valid_input_output_data(self, input_volume_node, output_volume_node):
        """Validates if the output is not the same as input"""
        if not input_volume_node:
            logging.debug("is_valid_input_output_data failed: no input volume node defined")
            return False
        if not output_volume_node:
            logging.debug("is_valid_input_output_data failed: no output volume node defined")
            return False
        if input_volume_node.GetID() == output_volume_node.GetID():
            logging.debug(
                "is_valid_input_output_data failed: input and output volume is the same. Create a new volume for output to avoid this error."
            )
            return False
        return True

    def run(self, input_volume, output_volume, image_threshold):
        """Run the actual algorithm"""

        if not self.is_valid_input_output_data(input_volume, output_volume):
            slicer.util.errorDisplay("Input volume is the same as output volume. Choose a different output volume.")
            return False
        
        self.apply_threshold(input_volume, output_volume, image_threshold)
        return True
    
    def apply_threshold(self, input_volume, output_volume, image_threshold):
        
        # from vtk to numpy
        input_image_data = input_volume.GetImageData()
        input_array = vtk_np.vtk_to_numpy(input_image_data.GetPointData().GetScalars()) # 1d array
        
        # apply threshold
        threshold_value = image_threshold * input_array.max() 
        output_array = np.where(input_array.copy() > threshold_value, 255, 0)

        # from numpy back to vtk 
        output_image_data = vtk.vtkImageData()
        output_image_data.SetDimensions(input_image_data.GetDimensions())
        vtk_output_array = vtk_np.numpy_to_vtk(num_array=output_array.ravel(), deep=True, array_type=vtk.VTK_DOUBLE)
        output_image_data.GetPointData().SetScalars(vtk_output_array)

        # set output volume with the output data
        output_volume.SetAndObserveImageData(output_image_data)
        
        # update the scene
        slicer.mrmlScene.AddNode(output_volume)
        slicer.util.setSliceViewerLayers(background=output_volume)

        return True
    
class ProgrammingAssignmentPedroSansonTest(ScriptedLoadableModuleTest):
    """This is the test case for your scripted module.

    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_Skeleton1()

    def test_Skeleton1(self):
        pass
