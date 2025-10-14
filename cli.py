#!/usr/bin/env python3
"""
CarbonSaver CLI - Interactive Load Profile Optimizer
"""

from load_optimizer import compare_load_profiles


def get_user_input():
    """
    Get load profile parameters from user input.
    """
    print("\n🌱 CarbonSaver - Load Profile Optimizer")
    print("=" * 70)
    print("This tool helps you find the optimal time to run your load")
    print("to minimize carbon emissions.")
    print("=" * 70)

    # Get load profile parameters
    print("\nPlease enter your load profile details:\n")

    # Start hour
    while True:
        try:
            start_hour = int(input("Standard start hour (0-23, e.g., 7 for 7am): "))
            if 0 <= start_hour <= 23:
                break
            else:
                print("Please enter a value between 0 and 23")
        except ValueError:
            print("Please enter a valid number")

    # Duration
    while True:
        try:
            duration = int(input("Duration in hours (e.g., 4): "))
            if 1 <= duration <= 24:
                break
            else:
                print("Please enter a value between 1 and 24")
        except ValueError:
            print("Please enter a valid number")

    # Load
    while True:
        try:
            energy_mwh = float(input("Total energy consumption in MWh (e.g., 1.0): "))
            if energy_mwh > 0:
                # Calculate load in MW
                load_mw = energy_mwh / duration
                break
            else:
                print("Please enter a positive value")
        except ValueError:
            print("Please enter a valid number")

    return start_hour, duration, load_mw, energy_mwh


def main():
    """
    Main CLI interface.
    """
    # Get user input
    start_hour, duration, load_mw, energy_mwh = get_user_input()

    # Display summary
    print("\n" + "-" * 70)
    print("INPUT SUMMARY")
    print("-" * 70)
    print(f"Standard Start Time:  {start_hour:02d}:00")
    print(f"Duration:             {duration} hours")
    print(f"Total Energy:         {energy_mwh} MWh")
    print(f"Average Load:         {load_mw:.3f} MW")
    print("-" * 70)

    input("\nPress Enter to start optimization...")

    # Run optimization
    results = compare_load_profiles(
        standard_start_hour=start_hour, duration_hours=duration, load_mw=load_mw
    )

    if results:
        # Additional summary
        print("\n" + "=" * 70)
        print("💡 RECOMMENDATION")
        print("=" * 70)

        optimal = results["optimal"]
        time_shift = results["time_shift_hours"]

        if results["emissions_saved_kg"] > 1:
            print(
                f"\nShift your load to start at {optimal['start_time'].strftime('%H:%M')}"
            )
            print(f"(a shift of {time_shift:+.0f} hours from your standard schedule)")
            print(f"\nThis will save {results['emissions_saved_kg']:.2f} kg CO₂")
            print(f"({results['emissions_saved_pct']:.1f}% reduction in emissions)")

            # Convert to more relatable units
            if results["emissions_saved_kg"] > 1000:
                print(
                    f"\nThat's equivalent to {results['emissions_saved_kg']/1000:.2f} tonnes of CO₂!"
                )
            else:
                # Average car emits ~120g CO₂/km
                km_equivalent = results["emissions_saved_kg"] * 1000 / 120
                print(
                    f"\nThat's equivalent to driving {km_equivalent:.0f} km in a typical car!"
                )
        else:
            print("\nYour standard schedule is already near-optimal!")
            print(
                "There's minimal opportunity for emission reduction through time-shifting."
            )

        print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOptimization cancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        raise
