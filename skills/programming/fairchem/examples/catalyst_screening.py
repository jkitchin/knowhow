#!/usr/bin/env python3
"""
High-throughput catalyst screening using FAIRChem.

This example demonstrates screening multiple metal surfaces for CO adsorption
using FAIRChem's ultra-fast ML potentials. This would take days with DFT
but completes in minutes with FAIRChem.
"""

import numpy as np
from fairchem.core import pretrained_mlip, FAIRChemCalculator
from ase.build import fcc111, add_adsorbate
from ase.optimize import LBFGS
from ase.constraints import FixAtoms
from ase import Atoms


def calculate_adsorption_energy(
    metal,
    adsorbate="CO",
    surface_indices=(1, 1, 1),
    size=(4, 4, 4),
    adsorption_site="fcc",
    calculator=None,
    fmax=0.05,
):
    """
    Calculate adsorption energy using FAIRChem.

    Parameters
    ----------
    metal : str
        Metal element (e.g., 'Pt', 'Cu', 'Au')
    adsorbate : str
        Adsorbate molecule or atom
    surface_indices : tuple
        Miller indices of surface
    size : tuple
        Surface size (nx, ny, layers)
    adsorption_site : str
        Adsorption site ('fcc', 'hcp', 'ontop', 'bridge')
    calculator : FAIRChemCalculator
        Shared calculator instance
    fmax : float
        Force convergence criterion

    Returns
    -------
    dict
        Energies and adsorption energy
    """

    print(f"  Calculating {adsorbate} on {metal}({surface_indices})...")

    # Step 1: Clean surface
    slab = fcc111(metal, size=size, vacuum=10.0)

    # Fix bottom two layers
    n_atoms_per_layer = size[0] * size[1]
    constraint = FixAtoms(indices=range(n_atoms_per_layer * 2))
    slab.set_constraint(constraint)

    slab.calc = calculator

    # Optimize clean slab
    opt = LBFGS(slab, trajectory=f"{metal}_clean.traj", logfile=None)
    opt.run(fmax=fmax)
    E_slab = slab.get_potential_energy()

    # Step 2: Surface with adsorbate
    slab_ads = slab.copy()
    add_adsorbate(slab_ads, adsorbate, height=2.0, position=adsorption_site)
    slab_ads.set_constraint(constraint)
    slab_ads.calc = calculator

    opt = LBFGS(slab_ads, trajectory=f"{metal}_{adsorbate}.traj", logfile=None)
    opt.run(fmax=fmax)
    E_slab_ads = slab_ads.get_potential_energy()

    # Step 3: Isolated adsorbate
    if adsorbate in ["CO", "H2O", "CH4"]:
        from ase.build import molecule

        isolated = molecule(adsorbate)
    else:
        isolated = Atoms(adsorbate, positions=[(0, 0, 0)])

    isolated.center(vacuum=10.0)
    isolated.calc = calculator

    if len(isolated) > 1:
        opt = LBFGS(isolated, logfile=None)
        opt.run(fmax=fmax)

    E_adsorbate = isolated.get_potential_energy()

    # Adsorption energy
    E_ads = E_slab_ads - E_slab - E_adsorbate

    print(f"    {metal}: E_ads = {E_ads:.3f} eV")

    return {
        "metal": metal,
        "E_slab": E_slab,
        "E_slab_ads": E_slab_ads,
        "E_adsorbate": E_adsorbate,
        "E_adsorption": E_ads,
    }


def screen_metals(metals, adsorbate="CO", model_name="uma-m-1p1", use_turbo=False, workers=1):
    """
    Screen multiple metals for adsorption.

    Parameters
    ----------
    metals : list
        List of metal symbols to screen
    adsorbate : str
        Adsorbate to test
    model_name : str
        UMA model to use ('uma-s-1p2', 'uma-s-1p1', or 'uma-m-1p1')
    use_turbo : bool
        Enable turbo mode for speed
    workers : int
        Number of GPU workers for parallelization

    Returns
    -------
    list
        Results for each metal
    """

    print("=" * 60)
    print(f"High-Throughput Catalyst Screening with FAIRChem")
    print("=" * 60)
    print(f"Model: {model_name}")
    print(f"Adsorbate: {adsorbate}")
    print(f"Metals: {', '.join(metals)}")
    print(f"Turbo mode: {use_turbo}")
    print(f"Workers: {workers}")
    print("=" * 60)

    # Load model
    print("\nLoading FAIRChem model...")
    inference_settings = None
    if use_turbo:
        # Use turbo_umas for UMA-S models, turbo for others
        if model_name.startswith("uma-s"):
            inference_settings = "turbo_umas"
        else:
            inference_settings = "turbo"

    predictor = pretrained_mlip.get_predict_unit(
        model_name,
        inference_settings=inference_settings,
    )

    # Create calculator for catalysis (oc20)
    calc = FAIRChemCalculator(
        predictor,
        task_name="oc20",  # Catalysis domain
        workers=workers,
    )

    print("Model loaded successfully!\n")

    # Screen each metal
    results = []
    for metal in metals:
        try:
            result = calculate_adsorption_energy(
                metal=metal, adsorbate=adsorbate, calculator=calc, fmax=0.05
            )
            results.append(result)
        except Exception as e:
            print(f"    Error for {metal}: {e}")
            continue

    return results


def analyze_and_plot_results(results, adsorbate="CO"):
    """
    Analyze screening results and create plots.

    Parameters
    ----------
    results : list
        Results from screening
    adsorbate : str
        Adsorbate name for plot title
    """

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    # Sort by adsorption energy
    results_sorted = sorted(results, key=lambda x: x["E_adsorption"])

    # Print table
    print(f"\n{'Metal':<10} {'E_ads (eV)':<15} {'Binding':<15}")
    print("-" * 60)

    for res in results_sorted:
        binding = (
            "Strong"
            if res["E_adsorption"] < -2.0
            else "Moderate"
            if res["E_adsorption"] < -1.0
            else "Weak"
            if res["E_adsorption"] < 0
            else "Unfavorable"
        )

        print(f"{res['metal']:<10} {res['E_adsorption']:<15.3f} {binding:<15}")

    print("-" * 60)

    # Best catalyst
    best = results_sorted[0]
    print(f"\nBest catalyst: {best['metal']} (E_ads = {best['E_adsorption']:.3f} eV)")

    # Plot results
    try:
        import matplotlib.pyplot as plt

        metals = [r["metal"] for r in results_sorted]
        energies = [r["E_adsorption"] for r in results_sorted]

        fig, ax = plt.subplots(figsize=(10, 6))

        # Bar plot
        colors = ["green" if e < -1.0 else "orange" if e < 0 else "red" for e in energies]
        ax.bar(metals, energies, color=colors, alpha=0.7, edgecolor="black")

        # Reference line at 0
        ax.axhline(y=0, color="black", linestyle="--", alpha=0.5)

        # Labels
        ax.set_xlabel("Metal", fontsize=12)
        ax.set_ylabel("Adsorption Energy (eV)", fontsize=12)
        ax.set_title(
            f"{adsorbate} Adsorption Energy on Different Metals\n(FAIRChem Screening)", fontsize=14
        )
        ax.grid(True, alpha=0.3, axis="y")

        # Rotate x labels if many metals
        if len(metals) > 5:
            plt.xticks(rotation=45, ha="right")

        plt.tight_layout()
        plt.savefig(f"{adsorbate}_screening_results.png", dpi=300)
        print(f"\nPlot saved: {adsorbate}_screening_results.png")

    except ImportError:
        print("\nNote: Install matplotlib for visualization")

    print("=" * 60)


if __name__ == "__main__":
    # Example 1: Screen FCC metals for CO adsorption
    print("\nExample 1: Screening FCC metals for CO adsorption\n")

    metals_fcc = ["Cu", "Ag", "Au", "Pt", "Pd", "Ni"]

    results = screen_metals(
        metals=metals_fcc,
        adsorbate="CO",
        model_name="uma-m-1p1",  # Medium model for accuracy
        use_turbo=False,
        workers=1,
    )

    analyze_and_plot_results(results, adsorbate="CO")

    # Example 2: Fast screening with turbo mode
    # Uncomment to run:

    # print("\n\nExample 2: Fast screening with turbo mode\n")
    #
    # results_turbo = screen_metals(
    #     metals=["Cu", "Ag", "Au", "Pt", "Pd", "Ni", "Rh", "Ir"],
    #     adsorbate="CO",
    #     model_name="uma-s-1p2",  # Latest small model
    #     use_turbo=True,  # Maximum speed (turbo_umas)
    #     workers=4  # Use 4 GPUs if available
    # )
    #
    # analyze_and_plot_results(results_turbo, adsorbate="CO")

    print("\nCatalyst screening complete!")
    print("\nNOTE: This screening took minutes with FAIRChem.")
    print("      The same workflow would take days with DFT.")
    print("\nNext steps:")
    print("  1. Validate top candidates with DFT")
    print("  2. Run more detailed calculations (coverage, barriers)")
    print("  3. Explore different adsorbates")
