"""Focused benchmark: 1fs baseline vs 2fs+HBonds on WW H200 OpenCL."""
import os, sys, time, numpy as np, tempfile
os.environ['PYTHONNOUSERSITE'] = '1'
import openmm, torch
from openmm import unit, MonteCarloBarostat
from openmm.app import PDBFile, Modeller, Simulation, ForceField, PME, HBonds
from openmmml import MLPotential
from pdbfixer import PDBFixer

def log(msg):
    from datetime import datetime, timezone
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)

log(f"GPU: {torch.cuda.get_device_name(0)}")

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
fx.findMissingResidues()
fx.missingResidues = {}
fx.findNonstandardResidues()
fx.replaceNonstandardResidues()
fx.findMissingAtoms()
fx.addMissingAtoms()
fx.addMissingHydrogens(pH=7.0)
m = Modeller(fx.topology, fx.positions)
os.unlink(tmp)

pa = list(range(m.topology.getNumAtoms()))
ff = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
m.addSolvent(ff, padding=1.0 * unit.nanometer, ionicStrength=0.15 * unit.molar, model='tip3p')
log(f"System: {m.topology.getNumAtoms()} atoms")

for dt, constr, label in [(1.0, None, '1fs/no-constr'), (2.0, HBonds, '2fs/HBonds')]:
    mm_sys = ff.createSystem(m.topology, nonbondedMethod=PME,
                             nonbondedCutoff=1.0 * unit.nanometer,
                             constraints=constr, rigidWater=True)
    pot = MLPotential('mace-off24-medium')
    hy = pot.createMixedSystem(m.topology, mm_sys, pa, interpolate=False)
    hy.addForce(MonteCarloBarostat(1.0 * unit.atmosphere, 300.0 * unit.kelvin, 25))
    plat = openmm.Platform.getPlatformByName('OpenCL')
    integ = openmm.LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond,
                                             dt * unit.femtosecond)
    sim = Simulation(m.topology, hy, integ, plat, {})
    sim.context.setPositions(m.positions)
    sim.minimizeEnergy(maxIterations=200)
    sim.context.setVelocitiesToTemperature(300 * unit.kelvin)
    sim.step(50)  # warmup
    t0 = time.time()
    sim.step(200)
    el = time.time() - t0
    st = sim.context.getState(getPositions=True, getEnergy=True)
    pe = st.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
    pos = st.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    ok = not (np.any(np.isnan(pos)) or np.isnan(pe))
    ns = 200 * dt * 1e-6
    nsd = ns / el * 86400
    ms = el / 200 * 1000
    log(f"  {label}: {nsd:.2f} ns/day | {ms:.1f} ms/step | PE={pe:.0f} | stable={ok}")

log("DONE")
