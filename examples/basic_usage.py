#!/usr/bin/env python3
"""
Basic Usage Examples for EventHorizon

This script demonstrates the most common use cases for the eventHorizon
black hole visualization framework.
"""

import matplotlib.pyplot as plt
import eventHorizon

def basic_luminet_visualization():
    """Basic luminet-style black hole visualization."""
    print("Creating basic luminet-style visualization...")
    
    # Simple black hole visualization
    fig, ax = eventHorizon.draw_blackhole(
        mass=1.0,
        inclination=80.0,
        particle_count=10000
    )
    
    plt.title("Basic Luminet-Style Black Hole", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/basic_usage/basic_luminet.png', 
                facecolor='black', dpi=150)
    plt.show()
    
    return fig, ax

def plot_points_example():
    """Example using the plot_points function."""
    print("Creating plot_points example...")
    
    fig, ax = eventHorizon.plot_points(
        mass=1.0,
        inclination=80.0,
        particle_count=5000,
        power_scale=0.9
    )
    
    plt.title("Plot Points Example", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/basic_usage/plot_points.png', 
                facecolor='black', dpi=150)
    plt.show()
    
    return fig, ax

def isoradial_example():
    """Example of isoradial curves."""
    print("Creating isoradial curves...")
    
    fig, ax = eventHorizon.plot_isoradials(
        mass=1.0,
        inclination=80.0,
        radii=[10, 15, 20, 25, 30, 35, 40],
        show_labels=True
    )
    
    plt.title("Isoradial Curves", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/basic_usage/isoradials.png', 
                facecolor='black', dpi=150)
    plt.show()
    
    return fig, ax

def isoredshift_example():
    """Example of isoredshift curves."""
    print("Creating isoredshift curves...")
    
    fig, ax = eventHorizon.plot_isoredshifts(
        mass=1.0,
        inclination=80.0,
        particle_count=3000
    )
    
    plt.title("Isoredshift Curves", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/basic_usage/isoredshifts.png', 
                facecolor='black', dpi=150)
    plt.show()
    
    return fig, ax

def photon_sphere_example():
    """Example showing photon sphere."""
    print("Creating photon sphere visualization...")
    
    fig, ax = eventHorizon.plot_photon_sphere(
        mass=1.0,
        show_legend=True
    )
    
    plt.title("Photon Sphere and Event Horizon", color='white')
    plt.tight_layout()
    plt.savefig('results/examples/basic_usage/photon_sphere.png', 
                facecolor='black', dpi=150)
    plt.show()
    
    return fig, ax

def quick_comparison():
    """Quick comparison of different inclination angles."""
    print("Creating inclination comparison...")
    
    inclinations = [30, 60, 80, 90]
    results = eventHorizon.compare_inclinations(
        inclinations=inclinations,
        particle_count=5000
    )
    
    # Save each result
    for i, (fig, ax) in enumerate(results):
        plt.figure(fig.number)
        plt.tight_layout()
        plt.savefig(f'results/examples/basic_usage/inclination_{inclinations[i]}.png', 
                    facecolor='black', dpi=150)
        plt.show()
    
    return results

def main():
    """Run all basic examples."""
    print("EventHorizon Basic Usage Examples")
    print("=" * 40)
    
    # Create results directory
    import os
    os.makedirs('results/examples/basic_usage', exist_ok=True)
    
    # Run examples
    basic_luminet_visualization()
    plot_points_example()
    isoradial_example()
    isoredshift_example()
    photon_sphere_example()
    quick_comparison()
    
    print("\nAll basic examples completed!")
    print("Results saved to: results/examples/basic_usage/")

if __name__ == "__main__":
    main()