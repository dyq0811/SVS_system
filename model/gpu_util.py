#!/usr/bin/env python3

# Copyright 2020 The Johns Hopkins University (author: Jiatong Shi)

import os
import subprocess
import torch


def get_free_gpus():
    """ Get IDs of free GPUs using `nvidia-smi`.
    Returns:
        sorted list of GPUs which have no running process.
    """
    p = subprocess.Popen(
            ["nvidia-smi",
             "--query-gpu=index,gpu_bus_id",
             "--format=csv,noheader"],
            stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    gpus = {}
    for line in stdout.decode('utf-8').strip().split(os.linesep):
        if not line:
            continue
        idx, busid = line.strip().split(',')
        gpus[busid] = int(idx)
    p = subprocess.Popen(
            ["nvidia-smi",
             "--query-compute-apps=pid,gpu_bus_id",
             "--format=csv,noheader"],
            stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    for line in stdout.decode('utf-8').strip().split(os.linesep):
        if not line:
            continue
        pid, busid = line.strip().split(',')
        del gpus[busid]
    return sorted([gpus[busid] for busid in gpus])


def use_single_gpu():
    """ Use single GPU device.
    If CUDA_VISIBLE_DEVICES is set, select a device from the variable.
    Otherwise, get a free GPU device and use it.
    Returns:
        assigned GPU id.
    """
    cvd = os.environ.get('CUDA_VISIBLE_DEVICES')
    if cvd is None:
        # no GPUs are researved
        cvd = get_free_gpus()[::-1][0]
        # current device id must be changed
        torch.cuda.set_device(cvd)
    elif ',' in cvd:
        # multiple GPUs are researved
        cvd = int(cvd.split(',')[0])
        # current device id is 0
    else:
        # single GPU is reserved
        cvd = int(cvd)
        # current device id is 0
    # Use the GPU immediately
    torch.zeros(1, device="cuda")
    return cvd


if __name__ == '__main__':
    from system_info import print_system_info
    print_system_info()
    cvd = use_single_gpu()
    print(f"PID {os.getpid()} uses GPU {cvd}")
    subprocess.call("nvidia-smi")
    device = torch.device("cuda")