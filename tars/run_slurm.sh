#!/bin/bash
#SBATCH -J JOB_NAME
#SBATCH -p haswell_24c_ib_sm61,skylake_24c,haswell_24c,ivybridge_20c,sandybridge_16c
#SBATCH -N 1
#SBATCH -t 00:00:00
#SBATCH -e err.%j
#SBATCH -o out.o%j
#SBATCH --comment vasp


export I_MPI_DEBUG=5

NODES=${SLURM_JOB_NODELIST}
let NPROCS=${SLURM_JOB_NUM_NODES}*${SLURM_CPUS_ON_NODE}
DO_PARALLEL="srun -n ${NPROCS}"

cd ${SLURM_SUBMIT_DIR}
#EXECUTABLE="/home/jthlol/program/vasp.5.4.1_tim_pol2/bin/vasp_std"
#EXECUTABLE="/home/jjw876/vasp.6.3.1/bin/vasp_std"
EXECUTABLE="/apps/programs/vasp/vasp.5.4.4/bin/vasp_std"

# ASE
# vasp calcs mode: "slab", "vib", "sp", "charge", "dos", "wf", "gas", "fiscs"
VASP_MODE=slab                  # sub.sh가 이 줄을 자동으로 변경합니다
export VASP_PP_PATH=/home/aracho/bin/potpaw_PBE.54 #POTCAR 폴더 위치
export VASP_SCRIPT=./run_vasp.py
echo "import os" > run_vasp.py
echo "exitcode = os.system('${DO_PARALLEL} ${EXECUTABLE}')" >> run_vasp.py

python ase_vasp.py $VASP_MODE   # 계산실행파일
python $play/vasp/get_restart.py
