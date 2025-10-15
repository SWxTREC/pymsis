project(
  'pymsis',
  'c',
  # Note that the git commit hash cannot be added dynamically here
  version: run_command('python', '-m', 'setuptools_scm', check: true).stdout().strip(),
  license: 'MIT',
  meson_version: '>=1.2.99',
  default_options: [
    'buildtype=release',
    'fortran_std=legacy',
  ],
)

cc = meson.get_compiler('c')

# TODO: the below -Wno flags are all needed to silence warnings in
# f2py-generated code. This should be fixed in f2py itself.
_global_c_args = cc.get_supported_arguments(
  '-Wno-unused-but-set-variable',
  '-Wno-unused-function',
  '-Wno-conversion',
  '-Wno-misleading-indentation',
  '-Wno-incompatible-pointer-types',
)
add_project_arguments(_global_c_args, language : 'c')


# Adding at project level causes many spurious -lgfortran flags.
add_languages('fortran', native: false)
ff = meson.get_compiler('fortran')
if ff.has_argument('-Wno-conversion')
  add_project_arguments('-Wno-conversion', language: 'fortran')
endif

# fast-math optimizations add a pretty significant speed-up.
# Tests fail on linux aarch64, so don't add the flag there
if ff.has_argument('-ffast-math')
  add_project_arguments('-ffast-math', language: 'fortran')
endif

is_windows = host_machine.system() == 'windows'
# Platform detection
is_mingw = is_windows and cc.get_id() == 'gcc'
if is_windows
  # Default to optimization level 0 on Windows only
  # Some CI jobs fail with higher levels of optimization, so restrict this by default.
  add_project_arguments('-O0', language: 'fortran')

  # Need static libraries to get libgfortran
  gcc_link_args = ['-static']
  if is_mingw
    add_project_link_arguments(gcc_link_args, language: ['c'])
  endif
  if meson.get_compiler('fortran').get_id() == 'gcc'
    add_project_link_arguments(gcc_link_args, language: ['fortran'])
  endif
endif

generate_f2pymod = files('tools/generate_f2pymod.py')

# https://mesonbuild.com/Python-module.html
py_mod = import('python')
py3 = py_mod.find_installation(pure: false)
py3_dep = py3.dependency()

incdir_numpy = run_command(py3,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

inc_np = declare_dependency(
  compile_args: ['-I' + incdir_numpy]
)

incdir_f2py = incdir_numpy / '..' / '..' / 'f2py' / 'src'
inc_f2py = declare_dependency(
  compile_args: ['-I' + incdir_f2py]
)
fortranobject_c = incdir_f2py / 'fortranobject.c'

# Share this object across multiple modules.
fortranobject_lib = static_library('_fortranobject',
  fortranobject_c,
  dependencies: [py3_dep, inc_np, inc_f2py],
)
fortranobject_dep = declare_dependency(
  link_with: fortranobject_lib,
  dependencies: [inc_np, inc_f2py],
)

generate_f2pymod = files('tools/generate_f2pymod.py')

# Get the external sources
run_command(py3,
  files('tools/download_source.py'),
  check : true
)
# Must build the src extensions first
subdir('src')
subdir('pymsis')
subdir('tests')
