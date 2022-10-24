from subprocess import check_output


def run_command(cmd: str) -> str:
    result = check_output(cmd, shell=True)
    return result.decode('utf-8')
