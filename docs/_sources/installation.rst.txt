.. _installation:

Installation
============

The following instructions cover dependency installation on Linux with
``apt-get`` and on macOS with Homebrew or MacPorts. Package managers such as
Anaconda, Miniforge, and Mamba might work, but they are not tested.

**plopm** supports Python 3.12 to 3.14.

.. _vplopm:

Python package
--------------

Install the development version of **plopm** in an existing Python
environment:

.. code-block:: console

   pip install git+https://github.com/cssr-tools/plopm.git

To install a specific version, modify the source code, or contribute to the
project, clone the repository and create a virtual environment:

.. code-block:: console

   # Clone the repository
   git clone https://github.com/cssr-tools/plopm.git

   # Enter the repository
   cd plopm

   # Optional: select a release, or skip this step to use the development version
   git checkout v2026.04

   # Create a virtual environment
   python3 -m venv vplopm

   # Activate the virtual environment
   source vplopm/bin/activate

   # Upgrade the packaging tools
   pip install --upgrade pip setuptools wheel

   # Install plopm in editable mode
   pip install -e .

   # Optional: install requirements for contributions, testing, and linting
   pip install -r dev-requirements.txt

.. tip::

   Run ``git tag -l`` to list the available releases.

Optional LaTeX formatting
-------------------------

LaTeX support is optional but recommended for figure formatting.

On Linux distributions using ``apt-get``, install:

.. code-block:: console

   sudo apt-get install texlive-fonts-recommended texlive-fonts-extra dvipng cm-super

On macOS, install `MacTeX <https://www.tug.org/mactex/>`_.

.. _opm-flow-installation:

OPM Flow
--------

OPM Flow is required to convert OPM Flow output files such as ``.EGRID``,
``.INIT``, and ``.UNRST`` to VTK. Use OPM Flow Release 2026.04 or the current
master branches.

See the `OPM project website <https://opm-project.org/>`_ for general
information.

Binary packages
+++++++++++++++

See the OPM Flow `download and installation instructions
<https://opm-project.org/?page_id=36>`_ for binary packages on Ubuntu and Red
Hat Enterprise Linux. The same page describes other supported platforms,
including source builds and virtual-machine-based installations.

.. tip::

   The plopm `CI workflow
   <https://github.com/cssr-tools/plopm/blob/main/.github/workflows/CI.yml>`_
   shows the installation of OPM Flow binary packages, optional LaTeX
   libraries, and **plopm** on Ubuntu 26.04 with Python 3.14.

Source build on Linux
+++++++++++++++++++++

After installing the OPM `prerequisites
<https://opm-project.org/?page_id=239>`_, build Flow from the current master
branches with MPI support. The following commands create the executable at
``./build/opm-simulators/bin/flow``:

.. code-block:: bash

   CURRENT_DIRECTORY="$PWD"

   mkdir build

   for repo in common grid simulators
   do
       git clone https://github.com/OPM/opm-$repo.git
       mkdir build/opm-$repo
       cd build/opm-$repo
       cmake -DUSE_MPI=1 -DWITH_NDEBUG=1 -DCMAKE_BUILD_TYPE=Release $CURRENT_DIRECTORY/opm-$repo
       if [[ $repo == simulators ]]; then
           make -j5 flow
       else
           make -j5 opm$repo
       fi
       cd ../..
   done

.. tip::

   Save the commands in a shell script, for example
   ``build_opm_mpi.sh``, and run it with:

   .. code-block:: console

      . ./build_opm_mpi.sh

The resulting Flow executable can be selected explicitly when generating VTK
files:

.. code-block:: console

   plopm -i SPE11C -m vtk -fp ./build/opm-simulators/bin/flow

See :option:`plopm -fp` and :ref:`options-vtk`.

.. _macOS:

Homebrew formula for macOS
++++++++++++++++++++++++++

Binary OPM Flow packages are not available for macOS, so Flow must be built
from source. The `cssr-tools/homebrew-opm
<https://github.com/cssr-tools/homebrew-opm>`_ repository provides a Homebrew
formula for this purpose.

Install the OPM Flow v2026.07 interim release with:

.. code-block:: console

   brew tap cssr-tools/opm
   brew trust cssr-tools/opm
   brew install cssr-tools/opm/opm-simulators -y

Verify the installation:

.. code-block:: console

   flow --help

.. tip::

   See the `homebrew-opm workflow results
   <https://github.com/cssr-tools/homebrew-opm/actions>`_ for tested builds.

Source build on macOS
+++++++++++++++++++++

See the `OPM-Flow_macOS repository
<https://github.com/daavid00/OPM-Flow_macOS>`_ for a source-build workflow for
OPM Flow on macOS 26. The workflow runs with GitHub Actions and is tested with
**pycopm**, another project in the ``cssr-tools`` organization.

Next steps
----------

* Follow the :doc:`tutorial` to progress from a first PNG to SPE11C
  projections and comparisons.
* Browse the :doc:`examples` for task-oriented workflows.
* Use the :doc:`command-line` for syntax and option descriptions.
