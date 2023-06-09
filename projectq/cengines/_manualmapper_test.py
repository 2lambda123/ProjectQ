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
"""Tests for projectq.cengines._manualmapper.py."""

from projectq import MainEngine
from projectq.cengines import DummyEngine, ManualMapper
from projectq.meta import LogicalQubitIDTag
from projectq.ops import All, H, Measure


def test_manualmapper_mapping():
    backend = DummyEngine(save_commands=True)

    def mapping(qubit_id):
        return (qubit_id + 1) & 1

    eng = MainEngine(backend=backend, engine_list=[ManualMapper(mapping)])
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    H | qb0
    H | qb1
    All(Measure) | (qb0 + qb1)
    eng.flush()

    num_measurements = 0
    for cmd in backend.received_commands:
        if cmd.gate == Measure:
            tag = LogicalQubitIDTag(mapping(cmd.qubits[0][0].id))
            assert tag in cmd.tags
            wrong_tag = LogicalQubitIDTag(cmd.qubits[0][0].id)
            assert wrong_tag not in cmd.tags
            num_measurements += 1
    assert num_measurements == 2
