"""
Combined diagnostic: float32 e3nn patch + openequivariance acceleration.
Tests force correctness and throughput vs baseline.
"""
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'

import torch
import e3nn.o3._wigner as _w

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"GPU: {torch.cuda.get_device_name(0)}")

# --- Float32 e3nn patch ---
log("Patching e3nn Wigner constants to float32...")
_w._Jd = [j.to(torch.float32) for j in _w._Jd]
_w._W3j_flat = _w._W3j_flat.to(torch.float32)
log(f"  _Jd[0] dtype: {_w._Jd[0].dtype}, _W3j_flat dtype: {_w._W3j_flat.dtype}")

# --- Check openequivariance ---
try:
    import openequivariance as oeq
    OEQ_AVAILABLE = True
    log(f"openequivariance available (version {oeq.__version__})")
except ImportError:
    OEQ_AVAILABLE = False
    log("openequivariance NOT available — testing float32 only")

# --- Build WW system ---
log("Building WW system...")
import openmm
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME
from openmmml import MLPotential
from pdbfixer import PDBFixer

pdb = PDBFile("/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-0/subphase-0.1/proteins/ww.pdb")
m = Modeller(pdb.topology, pdb.positions)
std = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS',
       'MET','PHE','PRO','SER','THR','TRP','TYR','VAL','HID','HIE','HIP','CYX',
       'CYM','ASH','GLH','LYN'}
m.delete([r for r in m.topology.residues() if r.name not in std])
ch0 = list(m.topology.chains())[0].id
oth = []
for c in m.topology.chains():
    if c.id != ch0:
        oth.extend(c.residues())
if oth:
    m.delete(oth)
m.delete([r for r in m.topology.residues() if int(r.id) < 6 or int(r.id) > 39])
with tempfile.NamedTemporaryFile(suffix='.pdb', mode='w', delete=False) as f:
    PDBFile.writeFile(m.topology, m.positions, f)
    tmp = f.name
fx = PDBFixer(filename=tmp)
fx.findMissingResidues(); fx.missingResidues = {}
fx.findNonstandardResidues(); fx.replaceNonstandardResidues()
fx.findMissingAtoms(); fx.addMissingAtoms(); fx.addMissingHydrogens(pH=7.0)
m = Modeller(fx.topology, fx.positions)
os.unlink(tmp)
pa = list(range(m.topology.getNumAtoms()))
n_prot = len(pa)
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0*unit.nanometer, ionicStrength=0.15*unit.molar, model='tip3p')
log(f"System: {m.topology.getNumAtoms()} atoms (protein={n_prot})")

def run_benchmark(label, precision_kwarg, use_oeq=False):
    """Build hybrid system + run 50 steps, report throughput."""
    try:
        mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME,
                                 nonbondedCutoff=1.0*unit.nanometer,
                                 constraints=None, rigidWater=True)
        pot = MLPotential('mace-off24-medium')
        hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False,
                                   **precision_kwarg)

        # If oeq requested, find the PythonForce and convert its model
        if use_oeq and OEQ_AVAILABLE:
            # The model is captured inside the PythonForce's partial function
            # We need to convert it before the first force evaluation
            # This is tricky — let's try a different approach:
            # Load model separately, convert, then monkey-patch
            from mace.calculators.foundations_models import mace_off
            from mace.cli.convert_e3nn_oeq import run as run_e3nn_to_oeq
            device = 'cuda'
            raw_model = mace_off(
                model='https://github.com/ACEsuit/mace-off/blob/main/mace_off24/MACE-OFF24_medium.model?raw=true',
                device=device, return_raw_model=True).to(device)
            if precision_kwarg.get('precision') == 'single':
                raw_model = raw_model.to(torch.float32)
            oeq_model = run_e3nn_to_oeq(raw_model, device=device).to(device)
            for p in oeq_model.parameters():
                p.requires_grad = False
            # Replace model in the PythonForce callback
            for i in range(hy.getNumForces()):
                force = hy.getForce(i)
                if isinstance(force, openmm.PythonForce):
                    # Access the partial function and replace the model
                    cb = force.getComputeFunction()
                    if hasattr(cb, 'keywords') and 'model' in cb.keywords:
                        cb.keywords['model'] = oeq_model
                        log(f"  Replaced model with oeq-converted version")
                    break

        hy.addForce(MonteCarloBarostat(1.0*unit.atmosphere, 300.0*unit.kelvin, 25))
        plat = openmm.Platform.getPlatformByName('OpenCL')
        integ = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1.0/unit.picosecond,
                                                 1.0*unit.femtosecond)
        sim = Simulation(m.topology, hy, integ, plat, {})
        sim.context.setPositions(m.positions)

        sim.minimizeEnergy(maxIterations=200)
        state = sim.context.getState(getForces=True)
        max_f = float(np.max(np.abs(
            state.getForces(asNumpy=True).value_in_unit(unit.kilojoules_per_mole/unit.nanometer))))
        if max_f > 1e5:
            log(f"  {label}: FAIL post-min force {max_f:.2e}")
            return
        sim.context.setVelocitiesToTemperature(300*unit.kelvin)
        sim.step(20)  # warmup
        t0 = time.time()
        sim.step(50)
        el = time.time() - t0
        st = sim.context.getState(getPositions=True, getEnergy=True)
        pe = st.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        pos = st.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        if np.any(np.isnan(pos)) or np.isnan(pe):
            log(f"  {label}: FAIL NaN")
            return
        nsd = 50*1e-6/el*86400
        log(f"  {label}: {nsd:.2f} ns/day | {el/50*1000:.1f} ms/step | F={max_f:.0e} | PE={pe:.0f}")
    except Exception as e:
        log(f"  {label}: ERROR — {e}")
        import traceback; traceback.print_exc()

# --- Benchmarks ---
log("--- Benchmarks (50 steps each) ---")

# A: Baseline (f64, current production)
run_benchmark("A: f64 baseline", {})

# B: Float32 only (e3nn patch applied above)
run_benchmark("B: f32 (e3nn patched)", {'precision': 'single'})

# C: Float32 + openequivariance (if available)
if OEQ_AVAILABLE:
    run_benchmark("C: f32 + oeq", {'precision': 'single'}, use_oeq=True)
else:
    log("  C: SKIPPED (openequivariance not installed)")

log("=== DONE ===")
