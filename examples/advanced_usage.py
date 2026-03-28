#!/usr/bin/env python3
"""
Advanced Usage Examples for EventHorizon

This script demonstrates advanced features and customization options
for the eventHorizon black hole visualization framework.
"""

import matplotlib.pyplot as plt
import numpy as np
import eventHorizon

def high_quality_visualization():
    """High-quality visualization with enhanced parameters."""
    print("Creating high-quality visualization...")
    
    fig, ax = eventHorizon.high_quality_blackhole(
        inclination=85.0,
        particle_count=50000,
        power_scale=0.8,
        levels=200,
        figsize=(12, 12),
        ax_lim=(-50, 50)
    )
    
    plt.title("High-Quality Luminet Visualization", color='white', fontsize=16)
    plt.tight_layout()
    plt.savefig('results/examples/advanced/high_quality.png', 
                facecolor='black', dpi=300)
    plt.show()
    
    return fig, ax

def custom_parameters_example():
    """Example with custom parameters and styling."""
    print("Creating custom parameters example...")
    
    # Custom visualization with specific parameters
    fig, ax = eventHorizon.draw_blackhole(
        mass=2.0,  # Larger black hole
        inclination=75.0,
        particle_count=20000,
        power_scale=0.7,
        levels=150,
        figsize=(10, 10),
        ax_lim=(-60, 60),
        accretion_rate=1.5,
        show_ghost_image=True,
        show_title=True,
        title="Custom Black Hole (M=2.0, i=75°)"
    )
    
    plt.tight_layout()
    plt.savefig('results/examples/advanced/custom_parameters.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, ax

def parameter_study():
    """Study the effect of different parameters."""
    print("Creating parameter study...")
    
    # Study different power scales
    power_scales = [0.5, 0.7, 0.9, 1.1]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    for i, power_scale in enumerate(power_scales):
        row, col = i // 2, i % 2
        
        # Create visualization with specific power scale
        temp_fig, temp_ax = eventHorizon.draw_blackhole(
            mass=1.0,
            inclination=80.0,
            particle_count=8000,
            power_scale=power_scale,
            levels=100
        )
        
        # Copy the content to subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        
        # Get the data from temp_ax and plot on axes[row, col]
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'Power Scale = {power_scale}', color='white')
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/advanced/power_scale_study.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def mass_comparison():
    """Compare different black hole masses."""
    print("Creating mass comparison...")
    
    masses = [0.5, 1.0, 2.0, 5.0]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    for i, mass in enumerate(masses):
        row, col = i // 2, i % 2
        
        # Create visualization with specific mass
        temp_fig, temp_ax = eventHorizon.draw_blackhole(
            mass=mass,
            inclination=80.0,
            particle_count=8000,
            power_scale=0.9,
            ax_lim=(-40, 40)
        )
        
        # Copy the content to subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        
        # Get the data from temp_ax and plot on axes[row, col]
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'Mass = {mass}M☉', color='white')
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/advanced/mass_comparison.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def combined_visualization():
    """Combined visualization showing multiple elements."""
    print("Creating combined visualization...")
    
    # Create base black hole visualization
    fig, ax = eventHorizon.draw_blackhole(
        mass=1.0,
        inclination=80.0,
        particle_count=15000,
        power_scale=0.9,
        figsize=(12, 12),
        ax_lim=(-45, 45)
    )
    
    # Add photon sphere
    photon_sphere_radius = 3.0
    circle = plt.Circle((0, 0), photon_sphere_radius, 
                       fill=False, color='red', linestyle='--', 
                       linewidth=2, alpha=0.6, label='Photon Sphere')
    ax.add_patch(circle)
    
    # Add event horizon
    event_horizon_radius = 2.0
    horizon_circle = plt.Circle((0, 0), event_horizon_radius, 
                               fill=True, color='black', 
                               edgecolor='white', linewidth=1,
                               alpha=1.0, label='Event Horizon')
    ax.add_patch(horizon_circle)
    
    # Add some isoradial curves
    from eventHorizon.math.geodesics import UnifiedGeodesics
    
    geodesics = UnifiedGeodesics(mass=1.0)
    inclination_rad = 80.0 * np.pi / 180
    
    for radius in [10, 20, 30]:
        angles = np.linspace(0, 2*np.pi, 100)
        impact_params = []
        
        for angle in angles:
            try:
                b = geodesics.calculate_impact_parameter(
                    angle, radius, inclination_rad, image_order=0
                )
                impact_params.append(b if b is not None else 0)
            except Exception:
                impact_params.append(0)
        
        x = [b * np.cos(a - np.pi/2) for b, a in zip(impact_params, angles) if b > 0]
        y = [b * np.sin(a - np.pi/2) for b, a in zip(impact_params, angles) if b > 0]
        
        if x and y:
            ax.plot(x, y, color='cyan', alpha=0.4, linewidth=1)
    
    ax.legend(loc='upper right')
    plt.title("Combined Visualization", color='white', fontsize=16)
    plt.tight_layout()
    plt.savefig('results/examples/advanced/combined_visualization.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, ax

def performance_benchmark():
    """Benchmark different particle counts."""
    print("Running performance benchmark...")
    
    import time
    
    particle_counts = [1000, 5000, 10000, 25000]
    times = []
    
    for count in particle_counts:
        print(f"  Testing {count} particles...")
        start_time = time.time()
        
        fig, ax = eventHorizon.draw_blackhole(
            mass=1.0,
            inclination=80.0,
            particle_count=count,
            power_scale=0.9
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        times.append(elapsed)
        
        plt.close(fig)
        print(f"    Time: {elapsed:.2f} seconds")
    
    # Plot benchmark results
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(particle_counts, times, 'bo-', linewidth=2, markersize=8)
    ax.set_xlabel('Particle Count')
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Performance Benchmark')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/examples/advanced/performance_benchmark.png', dpi=150)
    plt.show()
    
    return fig, ax, dict(zip(particle_counts, times))

def main():
    """Run all advanced examples."""
    print("EventHorizon Advanced Usage Examples")
    print("=" * 45)
    
    # Create results directory
    import os
    os.makedirs('results/examples/advanced', exist_ok=True)
    
    # Run examples
    high_quality_visualization()
    custom_parameters_example()
    parameter_study()
    mass_comparison()
    combined_visualization()
    benchmark_results = performance_benchmark()
    
    print("\nAll advanced examples completed!")
    print("Results saved to: results/examples/advanced/")
    print(f"Benchmark results: {benchmark_results[2]}")

if __name__ == "__main__":
    main()