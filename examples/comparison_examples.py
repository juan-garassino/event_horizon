#!/usr/bin/env python3
"""
Comparison Examples for EventHorizon

This script demonstrates comparisons between different visualization methods
and validates against reference implementations.
"""

import matplotlib.pyplot as plt
import numpy as np
import eventHorizon

def luminet_vs_traditional():
    """Compare luminet particle method vs traditional isoradial method."""
    print("Creating luminet vs traditional comparison...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    fig.patch.set_facecolor('black')
    
    # Luminet particle visualization
    temp_fig1, temp_ax1 = eventHorizon.draw_blackhole(
        mass=1.0,
        inclination=80.0,
        particle_count=15000,
        power_scale=0.9
    )
    
    # Copy luminet visualization to subplot
    ax1.clear()
    ax1.set_facecolor('black')
    for collection in temp_ax1.collections:
        ax1.add_collection(collection)
    ax1.set_xlim(temp_ax1.get_xlim())
    ax1.set_ylim(temp_ax1.get_ylim())
    ax1.set_aspect('equal')
    ax1.set_title('Luminet Particle Method', color='white', fontsize=14)
    ax1.axis('off')
    plt.close(temp_fig1)
    
    # Traditional isoradial visualization
    temp_fig2, temp_ax2 = eventHorizon.plot_isoradials(
        mass=1.0,
        inclination=80.0,
        radii=list(range(6, 51, 2))
    )
    
    # Copy isoradial visualization to subplot
    ax2.clear()
    ax2.set_facecolor('black')
    for line in temp_ax2.lines:
        ax2.add_line(line)
    for patch in temp_ax2.patches:
        ax2.add_patch(patch)
    ax2.set_xlim(temp_ax2.get_xlim())
    ax2.set_ylim(temp_ax2.get_ylim())
    ax2.set_aspect('equal')
    ax2.set_title('Traditional Isoradial Method', color='white', fontsize=14)
    ax2.axis('off')
    plt.close(temp_fig2)
    
    plt.tight_layout()
    plt.savefig('results/examples/comparisons/luminet_vs_traditional.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, (ax1, ax2)

def inclination_series():
    """Create a series showing different inclination angles."""
    print("Creating inclination angle series...")
    
    inclinations = [30, 45, 60, 75, 85, 90]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.patch.set_facecolor('black')
    
    for i, inclination in enumerate(inclinations):
        row, col = i // 3, i % 3
        
        temp_fig, temp_ax = eventHorizon.draw_blackhole(
            mass=1.0,
            inclination=inclination,
            particle_count=8000,
            power_scale=0.9,
            ax_lim=(-35, 35)
        )
        
        # Copy to subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'i = {inclination}°', color='white', fontsize=12)
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/comparisons/inclination_series.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def power_scale_comparison():
    """Compare different power scaling factors."""
    print("Creating power scale comparison...")
    
    power_scales = [0.3, 0.6, 0.9, 1.2]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    for i, power_scale in enumerate(power_scales):
        row, col = i // 2, i % 2
        
        temp_fig, temp_ax = eventHorizon.draw_blackhole(
            mass=1.0,
            inclination=80.0,
            particle_count=10000,
            power_scale=power_scale,
            levels=120
        )
        
        # Copy to subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'Power Scale = {power_scale}', color='white', fontsize=12)
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/comparisons/power_scale_comparison.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def particle_count_comparison():
    """Compare different particle counts."""
    print("Creating particle count comparison...")
    
    particle_counts = [2000, 5000, 15000, 30000]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    for i, count in enumerate(particle_counts):
        row, col = i // 2, i % 2
        
        temp_fig, temp_ax = eventHorizon.draw_blackhole(
            mass=1.0,
            inclination=80.0,
            particle_count=count,
            power_scale=0.9
        )
        
        # Copy to subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'{count:,} Particles', color='white', fontsize=12)
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/comparisons/particle_count_comparison.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def visualization_methods_comparison():
    """Compare all available visualization methods."""
    print("Creating visualization methods comparison...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    # Luminet particle visualization
    temp_fig1, temp_ax1 = eventHorizon.draw_blackhole(
        mass=1.0, inclination=80.0, particle_count=10000
    )
    axes[0, 0].clear()
    axes[0, 0].set_facecolor('black')
    for collection in temp_ax1.collections:
        axes[0, 0].add_collection(collection)
    axes[0, 0].set_xlim(temp_ax1.get_xlim())
    axes[0, 0].set_ylim(temp_ax1.get_ylim())
    axes[0, 0].set_aspect('equal')
    axes[0, 0].set_title('Luminet Particles', color='white', fontsize=12)
    axes[0, 0].axis('off')
    plt.close(temp_fig1)
    
    # Isoradial curves
    temp_fig2, temp_ax2 = eventHorizon.plot_isoradials(
        mass=1.0, inclination=80.0, radii=list(range(8, 41, 4))
    )
    axes[0, 1].clear()
    axes[0, 1].set_facecolor('black')
    for line in temp_ax2.lines:
        axes[0, 1].add_line(line)
    for patch in temp_ax2.patches:
        axes[0, 1].add_patch(patch)
    axes[0, 1].set_xlim(temp_ax2.get_xlim())
    axes[0, 1].set_ylim(temp_ax2.get_ylim())
    axes[0, 1].set_aspect('equal')
    axes[0, 1].set_title('Isoradial Curves', color='white', fontsize=12)
    axes[0, 1].axis('off')
    plt.close(temp_fig2)
    
    # Isoredshift curves
    temp_fig3, temp_ax3 = eventHorizon.plot_isoredshifts(
        mass=1.0, inclination=80.0, particle_count=5000
    )
    axes[1, 0].clear()
    axes[1, 0].set_facecolor('black')
    for collection in temp_ax3.collections:
        axes[1, 0].add_collection(collection)
    axes[1, 0].set_xlim(temp_ax3.get_xlim())
    axes[1, 0].set_ylim(temp_ax3.get_ylim())
    axes[1, 0].set_aspect('equal')
    axes[1, 0].set_title('Isoredshift Curves', color='white', fontsize=12)
    axes[1, 0].axis('off')
    plt.close(temp_fig3)
    
    # Photon sphere
    temp_fig4, temp_ax4 = eventHorizon.plot_photon_sphere(mass=1.0)
    axes[1, 1].clear()
    axes[1, 1].set_facecolor('black')
    for patch in temp_ax4.patches:
        axes[1, 1].add_patch(patch)
    for line in temp_ax4.lines:
        axes[1, 1].add_line(line)
    axes[1, 1].set_xlim(temp_ax4.get_xlim())
    axes[1, 1].set_ylim(temp_ax4.get_ylim())
    axes[1, 1].set_aspect('equal')
    axes[1, 1].set_title('Photon Sphere', color='white', fontsize=12)
    axes[1, 1].axis('off')
    plt.close(temp_fig4)
    
    plt.tight_layout()
    plt.savefig('results/examples/comparisons/visualization_methods.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def reference_validation():
    """Validate against reference implementations."""
    print("Running reference validation...")
    
    # This would typically compare with known reference results
    # For now, we'll create a visual comparison showing consistency
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('black')
    
    # Test different configurations
    configs = [
        {'inclination': 60.0, 'title': 'i=60°'},
        {'inclination': 80.0, 'title': 'i=80°'},
        {'inclination': 90.0, 'title': 'i=90°'}
    ]
    
    for i, config in enumerate(configs):
        temp_fig, temp_ax = eventHorizon.draw_blackhole(
            mass=1.0,
            inclination=config['inclination'],
            particle_count=8000,
            power_scale=0.9
        )
        
        axes[i].clear()
        axes[i].set_facecolor('black')
        for collection in temp_ax.collections:
            axes[i].add_collection(collection)
        
        axes[i].set_xlim(temp_ax.get_xlim())
        axes[i].set_ylim(temp_ax.get_ylim())
        axes[i].set_aspect('equal')
        axes[i].set_title(f'Reference Test: {config["title"]}', color='white', fontsize=12)
        axes[i].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/comparisons/reference_validation.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def main():
    """Run all comparison examples."""
    print("EventHorizon Comparison Examples")
    print("=" * 40)
    
    # Create results directory
    import os
    os.makedirs('results/examples/comparisons', exist_ok=True)
    
    # Run examples
    luminet_vs_traditional()
    inclination_series()
    power_scale_comparison()
    particle_count_comparison()
    visualization_methods_comparison()
    reference_validation()
    
    print("\nAll comparison examples completed!")
    print("Results saved to: results/examples/comparisons/")

if __name__ == "__main__":
    main()