.. _development:

Development
===========

To contribute to pymsis2, all you need to do is fork the GitHub repository,
add your code, and make a pull request. If you are adding additional functionality,
you should also include a test with your enhancement.

Pymsis2 is purposefully minimal, with numpy as the only dependency.
This makes it easy for other packages to leverage the interface to the Fortran
code without imposing a specific data storage or plotting framework.
