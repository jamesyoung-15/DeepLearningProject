# Detailed Project Setup Instructions
This project was built and tested with Linux (tried on Arch and Debian).

### Creating and Activating Environment (Optional)
[Python Virtual Environment Documentation](https://docs.python.org/3/library/venv.html)

Creating venv:
``` bash
python3 -m venv /path/to/new/virtual/environment
```

Activating venv:
``` bash
source <venv>/bin/activate
```

### Install Repo and Requirements
Make sure you at least have Python3, Pip, and Git.

```bash
# clone repo
git clone https://github.com/jamesyoung-15/DeepQLKart64
cd DeepQLKart64
# install requirements
pip install -r requirements.txt
```

For Mupen64Plus, there are many requirements. See their documentation below. Also ensure you have `binutils-dev` as I ran into issue on PopOS where it said no file "dis-asm.h" without it.

## Building Mupen64Plus from Source (Linux)
[Documentation on Compiling from Git.](https://mupen64plus.org/wiki/index.php/CompilingFromGit)
``` bash
cd mupen64plus-build
# allow script execution
chmod +x m64p_get.sh m64p_install.sh
# install mupen64plus git repo
./m64p_get.sh
# compile and build with debugging option
./m64p_build.sh DEBUG=1 DEBUGGER=1
# copy the core and plugin libraries over to m64py
./copy_files.sh
```
To check if the build was successful, you can run `./m64p_test.sh`.