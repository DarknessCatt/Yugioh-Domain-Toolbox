from cx_Freeze import setup, Executable

setup(
    name = "DomainGenerator",
    executables=[Executable("main.py", base="console")],
)