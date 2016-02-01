## Installation

(todo)

## Usage

Run:

    bk --help


## Adapters

The adapters are in development. They require HDF5 support.

    apt-get install libhdf5-dev
    pip install h5py
    
## Developing Adapters

Create a branch or fork of the repo.

First, create failing tests (yes, use TDD).

Start off with a specific model - e.g. linear regression, SVM - and get tests to pass for your adapter, before proceeding to another model type from the same library.

Document your code!

Once tests pass, create a pull request.
