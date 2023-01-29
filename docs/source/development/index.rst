.. _development:

Development
===========

To contribute to pymsis, you can fork the GitHub repository,
add your code, and make a pull request. If you are adding additional functionality,
you should also include a test with your enhancement.

Pymsis is purposefully minimal, with Numpy as the only dependency.
This makes it easy for other packages to leverage the interface to the Fortran
code without imposing a specific data storage or plotting framework.

A typical development workflow might look like the following:

.. code:: bash
    
    # Install the development dependencies
    pip install .[dev]

    # Install the pre-commit hooks
    pre-commit install

    # Update the code on a feature branch
    git checkout -b my-cool-feature

    # Run the tests
    pytest

    # Commit the changes and push to your remote repository
    git add my-file
    git commit
    git push -u origin my-cool-feature

    # Go to GitHub and open a pull request!
