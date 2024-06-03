# ******************************************************************************
#  Copyright (c) 2020 University of Stuttgart
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


class Result(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    result = db.Column(db.String(1200), default="")
    backend = db.Column(db.String(1200), default="")
    shots = db.Column(db.Integer, default=0)
    generated_circuit_id = db.Column(db.String(36), db.ForeignKey('generated__circuit.id'), nullable=True)
    post_processing_result = db.Column(db.String(1200), default="")
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return 'Result {}'.format(self.result)
