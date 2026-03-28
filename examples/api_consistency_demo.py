#!/usr/bin/env python3
"""
API Consistency Demonstration for EventHorizon

This script demonstrates the consistent API design across all visualization
methods in the eventHorizon framework.
"""

import matplotlib.pyplot as plt
import eventHorizon

def demonstrate_consistent_api():
    """Demonstrate consistent API across all visualization methods."""
    print("EventHorizon API Consistency Demonstration")
    print("=" * 50)
    
    # Common parameters used across all methods
    common_params = {
        'mass': 1.0,
        'inclination': 80.0,
        'figsize': (10, 10),
        'ax_lim': (-40, 40)
    }
    
    print(f"Using common parameters: {common_params}")
    print()
    
    # 1. Main luminet visualization
    print("1. Main luminet visualization (draw_blackhole)")
    fig1, ax1 = eventHorizon.draw_blackhole(
        **common_params,
        particle_count=10000,
        power_scale=0.9,
        levels=100
    )
    ax1.set_title("draw_blackhole()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/draw_blackhole.png', facecolor='black', dpi=150)
    plt.show()
    
    # 2. Plot points method
    print("2. Plot points method (plot_points)")
    fig2, ax2 = eventHorizon.plot_points(
        **common_params,
        particle_count=10000,
        power_scale=0.9
    )
    ax2.set_title("plot_points()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/plot_points.png', facecolor='black', dpi=150)
    plt.show()
    
    # 3. Isoradial curves
    print("3. Isoradial curves (plot_isoradials)")
    fig3, ax3 = eventHorizon.plot_isoradials(
        **common_params,
        radii=[10, 15, 20, 25, 30, 35, 40],
        show_labels=True
    )
    ax3.set_title("plot_isoradials()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/plot_isoradials.png', facecolor='black', dpi=150)
    plt.show()
    
    # 4. Isoredshift curves
    print("4. Isoredshift curves (plot_isoredshifts)")
    fig4, ax4 = eventHorizon.plot_isoredshifts(
        **common_params,
        particle_count=5000
    )
    ax4.set_title("plot_isoredshifts()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/plot_isoredshifts.png', facecolor='black', dpi=150)
    plt.show()
    
    # 5. Photon sphere
    print("5. Photon sphere (plot_photon_sphere)")
    fig5, ax5 = eventHorizon.plot_photon_sphere(
        mass=common_params['mass'],
        figsize=common_params['figsize'],
        ax_lim=(-10, 10),  # Smaller range for photon sphere
        show_legend=True
    )
    ax5.set_title("plot_photon_sphere()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/plot_photon_sphere.png', facecolor='black', dpi=150)
    plt.show()
    
    # 6. Apparent inner edge
    print("6. Apparent inner edge (plot_apparent_inner_edge)")
    fig6, ax6 = eventHorizon.plot_apparent_inner_edge(
        **common_params,
        show_legend=True
    )
    ax6.set_title("plot_apparent_inner_edge()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/plot_apparent_inner_edge.png', facecolor='black', dpi=150)
    plt.show()

def demonstrate_parameter_validation():
    """Demonstrate parameter validation across all methods."""
    print("\nParameter Validation Demonstration")
    print("=" * 40)
    
    # Test valid parameters
    print("✅ Testing valid parameters...")
    try:
        fig, ax = eventHorizon.draw_blackhole(mass=1.0, inclination=80.0, particle_count=5000)
        plt.close(fig)
        print("   Valid parameters accepted successfully")
    except Exception as e:
        print(f"   Unexpected error: {e}")
    
    # Test invalid mass
    print("\n❌ Testing invalid mass (negative)...")
    try:
        fig, ax = eventHorizon.draw_blackhole(mass=-1.0, inclination=80.0, particle_count=5000)
        plt.close(fig)
        print("   ERROR: Should have failed!")
    except ValueError as e:
        print("   Correctly caught invalid mass:")
        print(f"   {str(e)[:100]}...")
    
    # Test invalid inclination
    print("\n❌ Testing invalid inclination (out of range)...")
    try:
        fig, ax = eventHorizon.plot_isoradials(mass=1.0, inclination=200.0)
        plt.close(fig)
        print("   ERROR: Should have failed!")
    except ValueError as e:
        print("   Correctly caught invalid inclination:")
        print(f"   {str(e)[:100]}...")
    
    # Test invalid particle count
    print("\n❌ Testing invalid particle count (negative)...")
    try:
        fig, ax = eventHorizon.plot_points(mass=1.0, inclination=80.0, particle_count=-1000)
        plt.close(fig)
        print("   ERROR: Should have failed!")
    except ValueError as e:
        print("   Correctly caught invalid particle count:")
        print(f"   {str(e)[:100]}...")
    
    # Test warning conditions
    print("\n⚠️  Testing warning conditions...")
    try:
        fig, ax = eventHorizon.draw_blackhole(
            mass=1.0, 
            inclination=5.0,  # Extreme angle - should warn
            particle_count=100000  # Large count - should warn
        )
        plt.close(fig)
        print("   Warnings displayed for extreme parameters")
    except Exception as e:
        print(f"   Error: {e}")

def demonstrate_convenience_functions():
    """Demonstrate convenience functions."""
    print("\nConvenience Functions Demonstration")
    print("=" * 40)
    
    # Quick black hole
    print("1. Quick black hole (quick_blackhole)")
    fig1, ax1 = eventHorizon.quick_blackhole(inclination=75.0)
    ax1.set_title("quick_blackhole()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/quick_blackhole.png', facecolor='black', dpi=150)
    plt.show()
    
    # High quality black hole
    print("2. High quality black hole (high_quality_blackhole)")
    fig2, ax2 = eventHorizon.high_quality_blackhole(inclination=75.0)
    ax2.set_title("high_quality_blackhole()", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/api_demo/high_quality_blackhole.png', facecolor='black', dpi=150)
    plt.show()
    
    # Compare inclinations
    print("3. Compare inclinations (compare_inclinations)")
    results = eventHorizon.compare_inclinations([60, 80, 90])
    
    for i, (fig, ax) in enumerate(results):
        plt.figure(fig.number)
        plt.tight_layout()
        plt.savefig(f'results/examples/api_demo/compare_inclinations_{i}.png', facecolor='black', dpi=150)
        plt.show()

def demonstrate_return_value_consistency():
    """Demonstrate consistent return values across all methods."""
    print("\nReturn Value Consistency Demonstration")
    print("=" * 45)
    
    methods = [
        ('draw_blackhole', lambda: eventHorizon.draw_blackhole(particle_count=1000)),
        ('plot_points', lambda: eventHorizon.plot_points(particle_count=1000)),
        ('plot_isoradials', lambda: eventHorizon.plot_isoradials()),
        ('plot_isoredshifts', lambda: eventHorizon.plot_isoredshifts(particle_count=1000)),
        ('plot_photon_sphere', lambda: eventHorizon.plot_photon_sphere()),
        ('plot_apparent_inner_edge', lambda: eventHorizon.plot_apparent_inner_edge()),
        ('quick_blackhole', lambda: eventHorizon.quick_blackhole()),
        ('high_quality_blackhole', lambda: eventHorizon.high_quality_blackhole())
    ]
    
    for method_name, method_func in methods:
        try:
            result = method_func()
            
            # Check return type
            if isinstance(result, tuple) and len(result) == 2:
                fig, ax = result
                print(f"✅ {method_name:25} returns (Figure, Axes)")
                
                # Verify types
                if hasattr(fig, 'savefig') and hasattr(ax, 'plot'):
                    print(f"   {' ' * 25} Figure and Axes objects are valid")
                else:
                    print(f"   {' ' * 25} ❌ Invalid Figure or Axes objects")
                
                plt.close(fig)
            else:
                print(f"❌ {method_name:25} returns unexpected type: {type(result)}")
                
        except Exception as e:
            print(f"❌ {method_name:25} failed: {str(e)[:50]}...")

def main():
    """Run all API consistency demonstrations."""
    print("EventHorizon API Consistency and Validation Demo")
    print("=" * 55)
    
    # Create results directory
    import os
    os.makedirs('results/examples/api_demo', exist_ok=True)
    
    # Run demonstrations
    demonstrate_consistent_api()
    demonstrate_parameter_validation()
    demonstrate_convenience_functions()
    demonstrate_return_value_consistency()
    
    print("\n" + "=" * 55)
    print("API Consistency Demo Completed!")
    print("Results saved to: results/examples/api_demo/")
    print("\nKey API Features Demonstrated:")
    print("✅ Consistent parameter names across all methods")
    print("✅ Consistent return values (Figure, Axes)")
    print("✅ Comprehensive parameter validation with helpful errors")
    print("✅ Warning system for suboptimal parameters")
    print("✅ Convenience functions for common use cases")
    print("✅ Unified styling and behavior across all visualization types")

if __name__ == "__main__":
    main()