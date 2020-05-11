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

from urllib import request
import tempfile
import os, sys, shutil
from importlib import reload


def prepare_code_from_url(url, input_params):
    """Get implementation code from URL. Set input parameters into implementation. Return circuit"""
    impl = request.urlopen(url).read().decode("utf-8")
    print("Hier:" + impl)
    temp_dir = tempfile.mkdtemp()
    with open(os.path.join(temp_dir, "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join(temp_dir, "downloaded_code.py"), "w") as f:
        f.write(impl)
    sys.path.append(temp_dir)
    print(temp_dir)

    import downloaded_code

    reload(downloaded_code)
    circuit = downloaded_code.get_circuit(**input_params)
    print(circuit)

    sys.path.remove(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

    return circuit