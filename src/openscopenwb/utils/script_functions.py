import os 


def generate_module_cmd(module, input_json, output_json):
    """Generates a command string to use for subprocess calling

    Parameters
    ----------
    module: str
    The current module being run
    input_json: str
    The path of the input for the module
    output_json: str
    The path of the output for the module

    Returns
    -------
    command_string: str
    a string of the command string that will be used by the subprocess
    """
    conda_environment = 'openscopenwb'
    python_path = os.path.join(
        '/allen',
        'programs',
        'mindscope',
        'workgroups',
        'openscope',
        'ahad',
        'Conda_env',
        conda_environment,
        'bin',
        'python'
    )
    module_cmd = [python_path, "-W", "ignore", "-m", module,
                  "--input_json", input_json,
                  "--output_json", output_json]
    return module_cmd
