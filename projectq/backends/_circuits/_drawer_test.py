#   Copyright 2017, 2021 ProjectQ-Framework (www.projectq.ch)
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
Tests for projectq.backends.circuits._drawer.py.
"""

import pytest

import projectq.backends._circuits._drawer as _drawer
from projectq import MainEngine
from projectq.backends._circuits._drawer import CircuitDrawer, CircuitItem
from projectq.ops import CNOT, Command, H, Measure, X
from projectq.types import WeakQubitRef


class MockInputFunction:
    def __init__(self, return_value=None):
        self.return_value = return_value
        self._orig_input_fn = __builtins__['input']

    def _mock_input_fn(self, prompt):
        print(prompt + str(self.return_value))
        return self.return_value

    def __enter__(self):
        __builtins__['input'] = self._mock_input_fn

    def __exit__(self, type, value, traceback):
        __builtins__['input'] = self._orig_input_fn


@pytest.mark.parametrize("ordered", [False, True])
def test_drawer_getlatex(ordered):
    old_latex = _drawer.to_latex
    _drawer.to_latex = lambda x, drawing_order, draw_gates_in_parallel: x

    drawer = CircuitDrawer()
    drawer.set_qubit_locations({0: 1, 1: 0})

    drawer2 = CircuitDrawer()

    eng = MainEngine(drawer, [drawer2])
    qureg = eng.allocate_qureg(2)
    H | qureg[1]
    H | qureg[0]
    X | qureg[0]
    CNOT | (qureg[0], qureg[1])

    lines = drawer2.get_latex(ordered=ordered)
    assert len(lines) == 2
    assert len(lines[0]) == 4
    assert len(lines[1]) == 3

    # check if it was sent on correctly:
    lines = drawer.get_latex(ordered=ordered)
    assert len(lines) == 2
    assert len(lines[0]) == 3
    assert len(lines[1]) == 4

    _drawer.to_latex = old_latex


def test_drawer_measurement():
    drawer = CircuitDrawer(default_measure=0)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 0

    drawer = CircuitDrawer(default_measure=1)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 1

    drawer = CircuitDrawer(accept_input=True)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()

    with MockInputFunction(return_value='1'):
        Measure | qubit
        assert int(qubit) == 1

    qb1 = WeakQubitRef(engine=eng, idx=1)
    qb2 = WeakQubitRef(engine=eng, idx=2)
    with pytest.raises(ValueError):
        eng.backend._print_cmd(Command(engine=eng, gate=Measure, qubits=([qb1],), controls=[qb2]))


def test_drawer_qubitmapping():
    drawer = CircuitDrawer()
    # mapping should still work (no gate has been applied yet)
    valid_mappings = [{0: 1, 1: 0}, {2: 1, 1: 2}]
    for valid_mapping in valid_mappings:
        drawer.set_qubit_locations(valid_mapping)
        drawer = CircuitDrawer()

    # invalid mapping should raise an error:
    invalid_mappings = [{3: 1, 0: 2}, {0: 1, 2: 1}]
    for invalid_mapping in invalid_mappings:
        drawer = CircuitDrawer()
        with pytest.raises(RuntimeError):
            drawer.set_qubit_locations(invalid_mapping)

    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()  # noqa: F841
    # mapping has begun --> can't assign it anymore
    with pytest.raises(RuntimeError):
        drawer.set_qubit_locations({0: 1, 1: 0})


class MockEngine:
    def is_available(self, cmd):
        self.cmd = cmd
        self.called = True
        return False


def test_drawer_isavailable():
    drawer = CircuitDrawer()
    drawer.is_last_engine = True

    assert drawer.is_available(None)
    assert drawer.is_available("Everything")

    mock_engine = MockEngine()
    mock_engine.called = False
    drawer.is_last_engine = False
    drawer.next_engine = mock_engine

    assert not drawer.is_available(None)
    assert mock_engine.called
    assert mock_engine.cmd is None


def test_drawer_circuititem():
    circuit_item = CircuitItem(1, 2, 3)
    assert circuit_item.gate == 1
    assert circuit_item.lines == 2
    assert circuit_item.ctrl_lines == 3
    assert circuit_item.id == -1

    circuit_item2 = CircuitItem(1, 2, 2)
    assert not circuit_item2 == circuit_item
    assert circuit_item2 != circuit_item

    circuit_item2.ctrl_lines = 3
    assert circuit_item2 == circuit_item
    assert not circuit_item2 != circuit_item

    circuit_item2.gate = 2
    assert not circuit_item2 == circuit_item
    assert circuit_item2 != circuit_item

    circuit_item2.gate = 1
    assert circuit_item2 == circuit_item
    assert not circuit_item2 != circuit_item

    circuit_item2.lines = 1
    assert not circuit_item2 == circuit_item
    assert circuit_item2 != circuit_item

    circuit_item2.lines = 2
    assert circuit_item2 == circuit_item
    assert not circuit_item2 != circuit_item
