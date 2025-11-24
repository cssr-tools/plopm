============
Installation
============

The following steps work installing the dependencies in Linux via apt-get or in macOS using brew or macports.
While using packages managers such as Anaconda, Miniforge, or Mamba might work, these are not tested.
The supported Python versions are 3.11 to 3.14.

.. _vplopm:

Python package
--------------

To install the **plopm** executable from the development version in an existing Python environment: 

.. code-block:: bash

    pip install git+https://github.com/cssr-tools/plopm.git

If you are interested in a specific version (e.g., v2024.10) or in modifying the source code, then you can clone the repository and 
install the Python requirements in a virtual environment with the following commands:

.. code-block:: console

    # Clone the repo
    git clone https://github.com/cssr-tools/plopm.git
    # Get inside the folder
    cd plopm
    # For a specific version (e.g., v2024.10), or skip this step (i.e., edge version)
    git checkout v2024.10
    # Create virtual environment
    python3 -m venv vplopm
    # Activate virtual environment
    source vplopm/bin/activate
    # Upgrade pip, setuptools, and wheel
    pip install --upgrade pip setuptools wheel
    # Install the plopm package
    pip install -e .
    # For contributions/testing/linting, install the dev-requirements
    pip install -r dev-requirements.txt

.. tip::

    Typing **git tag -l** writes all available specific versions.

OPM Flow
--------
To use the convertion from OPM Flow output files (i.e., .EGRID, .INIT, .UNRST) to vtk, you also need to install:

* OPM Flow (https://opm-project.org, Release 2025.04 or current master branches)

.. tip::

    See the `CI.yml <https://github.com/cssr-tools/plopm/blob/main/.github/workflows/CI.yml>`_ script 
    for installation of OPM Flow (binary packages), LaTeX (optional) libraries, and the plopm package in Ubuntu.

Source build in Linux/Windows
+++++++++++++++++++++++++++++
If you are a Linux user (including the Windows subsystem for Linux), then you could try to build Flow (after installing the `prerequisites <https://opm-project.org/?page_id=239>`_) from the master branches with mpi support by running
in the terminal the following lines (which in turn should build flow in the folder ./build/opm-simulators/bin/flow): 

.. code-block:: console

    CURRENT_DIRECTORY="$PWD"

    mkdir build

    for repo in common grid
    do  git clone https://github.com/OPM/opm-$repo.git
        mkdir build/opm-$repo
        cd build/opm-$repo
        cmake -DUSE_MPI=1 -DWITH_NDEBUG=1 -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/build/opm-common;$CURRENT_DIRECTORY/build/opm-grid" $CURRENT_DIRECTORY/opm-$repo
        if [[ $repo == simulators ]]; then
            make -j5 flow
        else
            make -j5 opm$repo
        fi
        cd ../..
    done

.. tip::

    You can create a .sh file (e.g., build_opm_mpi.sh), copy the previous lines, and run in the terminal **source build_opm_mpi.sh**  

.. _macOS:

Source build in macOS
+++++++++++++++++++++
For macOS, there are no available binary packages, so OPM Flow needs to be built from source, in addition to the dune libraries 
(see the `prerequisites <https://opm-project.org/?page_id=239>`_, which can be installed using macports or brew). For example,
with brew the prerequisites can be installed by:

.. code-block:: console

    brew install boost openblas suite-sparse python@3.14 cmake

In addition, it is recommended to uprade and update your macOS to the latest available versions (the following steps have 
worked for macOS Tahoe 26.0.1 with Apple clang version 17.0.0).
After the prerequisites are installed and the vplopm Python environment is created (see :ref:`vplopm`), 
then building OPM Flow can be achieved with the following bash lines:

.. code-block:: console

    CURRENT_DIRECTORY="$PWD"

    deactivate
    source vplopm/bin/activate

    for module in common geometry grid istl
    do   git clone https://gitlab.dune-project.org/core/dune-$module.git --branch v2.9.1
        ./dune-common/bin/dunecontrol --only=dune-$module cmake -DCMAKE_DISABLE_FIND_PACKAGE_MPI=1
        ./dune-common/bin/dunecontrol --only=dune-$module make -j5
    done

    mkdir build

    for repo in common grid simulators
    do  git clone https://github.com/OPM/opm-$repo.git
        mkdir build/opm-$repo
        cd build/opm-$repo
        cmake -DUSE_MPI=0 -DWITH_NDEBUG=1 -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/dune-common/build-cmake;$CURRENT_DIRECTORY/dune-grid/build-cmake;$CURRENT_DIRECTORY/dune-geometry/build-cmake;$CURRENT_DIRECTORY/dune-istl/build-cmake;$CURRENT_DIRECTORY/build/opm-common;$CURRENT_DIRECTORY/build/opm-grid" $CURRENT_DIRECTORY/opm-$repo
        if [[ $repo == simulators ]]; then
            make -j5 flow
        else
            make -j5 opm$repo
        fi
        cd ../..
    done

    echo "export PATH=\$PATH:$CURRENT_DIRECTORY/build/opm-simulators/bin" >> $CURRENT_DIRECTORY/vplopm/bin/activate

    deactivate
    source vplopm/bin/activate


This builds OPM Flow, and it exports the path of the OPM Flow executable.

For macOS, the LaTeX dependency can be installed from https://www.tug.org/mactex/.

.. tip::
    See `this repository <https://github.com/daavid00/OPM-Flow_macOS>`_ dedicated to build OPM Flow from source in the latest macOS (GitHub actions), and tested with **pycopm**, another repository in cssr-tools.
    If you still face problems, raise an issue in the GitHub repository, or you could also send an email to the maintainers.
