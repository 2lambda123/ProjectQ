#   Copyright 2017 ProjectQ-Framework (www.projectq.ch)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Contains back-ends for ProjectQ.

This includes:

* a debugging tool to print all received commands (CommandPrinter)
* a circuit drawing engine (which can be used anywhere within the compilation
  chain)
* a simulator with emulation capabilities
* a resource counter (counts gates and keeps track of the maximal width of the
  circuit)
* an interface to the IBM Quantum Experience chip (and simulator).
* an interface to the AQT trapped ion system (and simulator).
* an interface to the AWS Braket service decives (and simulators)
* an interface to the Azure Quantum service devices (and simulators)
* an interface to the IonQ trapped ionq hardware (and simulator).
"""
from ._aqt import AQTBackend
from ._awsbraket import AWSBraketBackend
from ._azure import AzureQuantumBackend
from ._circuits import CircuitDrawer, CircuitDrawerMatplotlib
from ._exceptions import DeviceNotHandledError, DeviceOfflineError, DeviceTooSmall
from ._ibm import IBMBackend
from ._ionq import IonQBackend
from ._printer import CommandPrinter
from ._resource import ResourceCounter
from ._sim import ClassicalSimulator, Simulator
from ._unitary import UnitarySimulator
