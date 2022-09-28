# ******************************************************************************
#  Copyright (c) 2021 University of Stuttgart
#
#  See the NOTICE file(s) distributed with this work for additional
#  information regarding copyright ownership.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************

from app import db


class Benchmark(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    benchmark_id = db.Column(db.Integer)
    backend = db.Column(db.String(1200), default="")
    result = db.Column(db.String(1200), default="")
    counts = db.Column(db.String(1200), default="")
    shots = db.Column(db.Integer)
    original_depth = db.Column(db.Integer)
    original_width = db.Column(db.Integer)
    original_number_of_multi_qubit_gates = db.Column(db.Integer)
    transpiled_depth = db.Column(db.Integer)
    transpiled_width = db.Column(db.Integer)
    transpiled_number_of_multi_qubit_gates = db.Column(db.Integer)
    clifford = db.Column(db.Boolean)
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return 'Benchmark {}'.format(self.result)
