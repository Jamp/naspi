from psutil import disk_usage
from libs.utils import run_command


def get_temperature() -> float:
    cmd = 'vcgencmd measure_temp | grep  -o -E "[[:digit:]].*"'
    temp = run_command(cmd)
    return float(temp.replace('\'C', '').strip())


def hardware_stats() -> list:
    stats = []

    cmd = "echo $(vmstat 1 2|tail -1|awk '{print $15}')"
    idle = int(run_command(cmd))
    cpu_usage = float(100 - idle)

    cmd = "free | grep Mem | awk '{print $3/$2 * 100.0}'"
    free = float(run_command(cmd))

    stats.append(['CPU', cpu_usage])
    stats.append(['RAM', free])

    return stats


def disk_stats(mounted_point: list) -> list:
  disks = []

  for mount in mounted_point:
    total, _, _, percent = disk_usage(mount)

    disks.append([
      mount,
      '{:0.2f}GB'.format(total/(2**30)),
      '{:0.2f}%'.format(percent)
    ])

  return disks


def get_ip() -> str:
  cmd = "hostname -I | cut -d' ' -f1"
  return run_command(cmd)
