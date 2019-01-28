"""
Compute and Post-Processing Jobs for Vilma

Written by component_cookiecutter

----
"""

from pyesm.component.component_simulation import ComponentCompute
from pyesm.vilma import Vilma

class VilmaCompute(Vilma, ComponentCompute):
    """ A docstring. Please fill this out at least a little bit """

    def _compute_requirements(self):
        """ Compute requirements for Vilma """
        self.executeable = None
        self.command = None
        self.num_tasks = None
        self.num_threads = None

