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
import urllib.parse
from urllib import request, error
import tempfile
import os, sys, shutil
from importlib import reload
import qiskit




def prepare_code_from_data(data, input_params):
    """Get implementation code from data. Set input parameters into implementation. Return circuit."""
    temp_dir = tempfile.mkdtemp()
    with open(os.path.join(temp_dir, "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join(temp_dir, "downloaded_code.py"), "w") as f:
        f.write(data)
    sys.path.append(temp_dir)
    try:
        import downloaded_code

        # deletes every attribute from downloaded_code, except __name__, because importlib.reload
        # doesn't reset the module's global variables
        for attr in dir(downloaded_code):
            if attr != "__name__":
                delattr(downloaded_code, attr)

        reload(downloaded_code)
        if 'get_circuit' in dir(downloaded_code):
            circuit = downloaded_code.get_circuit(**input_params)
        elif 'qc' in dir(downloaded_code):
            circuit = downloaded_code.qc
    finally:
        sys.path.remove(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    if not circuit:
        raise ValueError
    return circuit


def prepare_code_from_url(url, input_params, bearer_token: str = ""):
    """Get implementation code from URL. Set input parameters into implementation. Return circuit."""
    try:
        impl = _download_code(url, bearer_token)
    except (error.HTTPError, error.URLError):
        return None

    circuit = prepare_code_from_data(impl, input_params)
    return circuit


def prepare_code_from_qasm(qasm):
    return qiskit.QuantumCircuit.from_qasm_str(qasm)


def prepare_code_from_qasm_url(url, bearer_token: str = ""):
    """Get implementation code from URL. Set input parameters into implementation. Return circuit."""
    try:
        impl = _download_code(url, bearer_token)
    except (error.HTTPError, error.URLError):
        return None

    return prepare_code_from_qasm(impl)


def _download_code(url: str, bearer_token: str = "") -> str:
    req = request.Request(url)

    if urllib.parse.urlparse(url).netloc == "platform.planqk.de":
        req.add_header("Authorization", bearer_token)

    res = request.urlopen(req)

    return res.read().decode("utf-8")
