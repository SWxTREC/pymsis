# msis00
msis00_module = custom_target('msis00_module',
    output: 'msis00fmodule.c',
    input: ['wrappers/msis00.pyf'],
    command: [py3, generate_f2pymod, '@INPUT@', '-o', '@OUTDIR@']
)

py3.extension_module('msis00f',
    ['msis00/NRLMSISE-00.FOR',
     'wrappers/msis00.F90',
     msis00_module,
    ],
    include_directories: [inc_np, inc_f2py],
    dependencies: fortranobject_dep,
    install: true,
    link_language: 'fortran',
    subdir: 'pymsis'
)

# msis2.0
msis20_module = custom_target('msis20_module',
    output: 'msis20fmodule.c',
    input: ['wrappers/msis20.pyf'],
    command: [py3, generate_f2pymod, '@INPUT@', '-o', '@OUTDIR@']
)

py3.extension_module('msis20f',
    ['wrappers/msis2.F90',
     'msis2.0/msis_constants.F90',
     'msis2.0/msis_init.F90',
     'msis2.0/msis_gfn.F90',
     'msis2.0/msis_tfn.F90',
     'msis2.0/alt2gph.F90',
     'msis2.0/msis_dfn.F90',
     'msis2.0/msis_calc.F90',
     msis20_module,
    ],
    include_directories: [inc_np, inc_f2py],
    dependencies: fortranobject_dep,
    install: true,
    link_language: 'fortran',
    subdir: 'pymsis'
)

# msis2.1
msis21_module = custom_target('msis21_module',
    output: 'msis21fmodule.c',
    input: ['wrappers/msis21.pyf'],
    command: [py3, generate_f2pymod, '@INPUT@', '-o', '@OUTDIR@']
)

py3.extension_module('msis21f',
    ['wrappers/msis2.F90',
     'msis2.1/msis_constants.F90',
     'msis2.1/msis_init.F90',
     'msis2.1/msis_gfn.F90',
     'msis2.1/msis_utils.F90',
     'msis2.1/msis_tfn.F90',
     'msis2.1/msis_dfn.F90',
     'msis2.1/msis_calc.F90',
     msis21_module,
    ],
    include_directories: [inc_np, inc_f2py],
    dependencies: fortranobject_dep,
    install: true,
    link_language: 'fortran',
    subdir: 'pymsis'
)