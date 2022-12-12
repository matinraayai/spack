# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Hipbone(MakefilePackage, ROCmPackage, CudaPackage):
    """HipBone is a GPU port of the original proxy application called Nekbone.
    It solves a screened Poisson equation in a box using a conjugate gradient method."""

    homepage = "https://github.com/paranumal/hipBone"
    git = "https://github.com/paranumal/hipBone.git"

    # notify when the package is updated.
    maintainers = ["matinraayai", "noelchalmers"]

    version("main")

    version("1.1.0", tag="v1.1.0", commit="e7c0c0641bc85295984e2bc67172392f45018074")

    variant("opencl", default=True, description="Builds with support for OpenCL")

    depends_on("openblas")
    depends_on("occa+rocm", when="+rocm")
    depends_on("occa+cuda", when="+cuda")
    depends_on("occa+opencl", when="+opencl")
    depends_on("mpi")

    def edit(self, spec, prefix):
        # Edits to make sure the kernel files can be read by the installed executable
        lib_makefile = FileFilter("./libs/makefile")
        lib_makefile.filter(
            r"LIBOGS_DIR=${HIPBONE_LIBS_DIR}/ogs",
            "LIBOGS_DIR=${HIPBONE_DIR}/libs/ogs",
            string=True,
        )

        make_top = FileFilter("./make.top")
        make_top.filter(
            r"export HIPBONE_DIR:="
            "$(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))",
            "export HIPBONE_REAL_DIR:="
            "$(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))\n"
            "export HIPBONE_DIR:=./",
            string=True,
        )
        make_top.filter(
            r"export HIPBONE_INCLUDE_DIR=${HIPBONE_DIR}/include",
            "export HIPBONE_INCLUDE_DIR=${HIPBONE_REAL_DIR}/include",
            string=True,
        )
        make_top.filter(
            r"export HIPBONE_LIBS_DIR=${HIPBONE_DIR}/libs",
            "export HIPBONE_LIBS_DIR=${HIPBONE_REAL_DIR}/libs",
            string=True,
        )
        # Edits to remove dependency on locally built OCCA
        make_file = FileFilter("./makefile")
        make_file.filter(r"${OCCA_DIR}", spec["occa"].prefix, string=True)
        make_file.filter(
            r"LIBS=-L${HIPBONE_LIBS_DIR} -lmesh -logs -lcore",
            "LIBS=-L${HIPBONE_LIBS_DIR} -lmesh -logs -lcore"
            f" -L{spec['occa'].prefix.lib}"
            f" -L{spec['openblas'].prefix.lib}",
        )
        make_file.filter(r"${MAKE} -C ${OCCA_DIR} clean", " ")
        make_file.filter(
            r"$(info OCCA_DIR  = $(OCCA_DIR))", "$(info OCCA_DIR  = " + spec["occa"].prefix + ")"
        )

    def setup_build_environment(self, env):
        env.set("PREFIX", self.prefix)

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        install("hipBone", prefix)
        install_tree("libs/", prefix.libs)
        install_tree("okl/", prefix.okl)
