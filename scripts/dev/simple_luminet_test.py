#!/usr/bin/env python3
"""
Simple Luminet Test - Create a basic black hole visualization
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add reference path to import Luminet modules
sys.path.append('references/luminet/core')
sys.path.append('references/luminet')

def create_simple_black_hole_image():
    """Create a simple black hole image using the core Luminet functions."""
    
    print("🔭 Creating simple black hole visualization...")
    
    try:
        from black_hole import BlackHole
        from bh_utils import polar_to_cartesian_lists
        
        # Change to luminet directory for parameters.ini
        original_dir = os.getcwd()
        os.chdir('references/luminet')
        
        # Create BlackHole with simpler parameters
        M = 1.0  # Simpler mass
        incl = 60  # Inclination in degrees
        
        bh = BlackHole(inclination=incl, mass=M)
        print(f"✅ Created BlackHole: M={M}, incl={incl}°")
        
        # Set simpler parameters
        bh.disk_outer_edge = 20 * M  # Smaller disk
        bh.disk_inner_edge = 6 * M
        
        print(f"   Disk: {bh.disk_inner_edge} to {bh.disk_outer_edge}")
        print(f"   Critical b: {bh.critical_b:.2f}")
        
        # Test coordinate transformation
        print("\n🔄 Testing coordinate transformation...")
        test_b = [5, 10, 15]
        test_angles = [0, np.pi/2, np.pi]
        
        x, y = polar_to_cartesian_lists(test_b, test_angles, rotation=-np.pi/2)
        print("   Transformed coordinates:")
        for i, (xi, yi) in enumerate(zip(x, y)):
            print(f"     b={test_b[i]}, θ={test_angles[i]:.2f} → ({xi:.1f}, {yi:.1f})")
        
        # Create a simple visualization manually
        print("\n🎨 Creating manual visualization...")
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        # Draw photon sphere (critical impact parameter)
        theta_circle = np.linspace(0, 2*np.pi, 100)
        x_photon = bh.critical_b * np.cos(theta_circle)
        y_photon = bh.critical_b * np.sin(theta_circle)
        ax.plot(x_photon, y_photon, 'red', linewidth=2, label='Photon Sphere')
        
        # Draw some sample isoradials manually
        print("   Drawing sample isoradials...")
        
        from bh_math import calc_impact_parameter
        
        radii_to_plot = [8, 12, 16]  # Different radii in the disk
        colors = ['cyan', 'yellow', 'magenta']
        
        for radius, color in zip(radii_to_plot, colors):
            angles = np.linspace(0, 2*np.pi, 50)
            x_iso = []
            y_iso = []
            
            for angle in angles:
                try:
                    # Calculate impact parameter for this radius and angle
                    b = calc_impact_parameter(radius, bh.t, angle, bh.M, 
                                            midpoint_iterations=10, 
                                            initial_guesses=8,
                                            min_periastron=3.1*bh.M)
                    if b is not None and b > 0:
                        # Convert to cartesian with critical rotation
                        x_pt, y_pt = polar_to_cartesian_lists([b], [angle], rotation=-np.pi/2)
                        x_iso.extend(x_pt)
                        y_iso.extend(y_pt)
                except:
                    continue
            
            if len(x_iso) > 2:
                ax.plot(x_iso, y_iso, color=color, alpha=0.7, linewidth=1.5, 
                       label=f'R = {radius}M')
                print(f"     ✅ Plotted isoradial R={radius}M with {len(x_iso)} points")
            else:
                print(f"     ❌ Not enough points for R={radius}M")
        
        # Set equal aspect ratio and limits
        max_lim = bh.critical_b * 1.5
        ax.set_xlim(-max_lim, max_lim)
        ax.set_ylim(-max_lim, max_lim)
        ax.set_aspect('equal')
        
        # Add labels and legend
        ax.legend(loc='upper right')
        ax.set_title('Simple Black Hole Visualization\n(Reference Luminet Implementation)', 
                    color='white', fontsize=14)
        
        # Save the plot
        os.chdir(original_dir)
        output_path = "simple_black_hole_test.png"
        fig.savefig(output_path, dpi=150, facecolor='black', bbox_inches='tight')
        plt.close(fig)
        
        print(f"✅ Saved visualization to {output_path}")
        
        # Test sampling a few points
        print("\n📊 Testing point sampling...")
        
        os.chdir('references/luminet')
        
        # Sample just a few points manually
        sample_points = []
        n_test = 20
        
        for i in range(n_test):
            # Random point in disk
            r = bh.disk_inner_edge + (bh.disk_outer_edge - bh.disk_inner_edge) * np.random.random()
            theta = np.random.random() * 2 * np.pi
            
            try:
                b = calc_impact_parameter(r, bh.t, theta, bh.M,
                                        midpoint_iterations=5,
                                        initial_guesses=6,
                                        min_periastron=3.1*bh.M)
                if b is not None and b > 0:
                    x, y = polar_to_cartesian_lists([b], [theta], rotation=-np.pi/2)
                    sample_points.append({
                        'r': r, 'theta': theta, 'b': b, 
                        'x': x[0], 'y': y[0]
                    })
            except:
                continue
        
        print(f"   Successfully sampled {len(sample_points)} points")
        
        if len(sample_points) > 0:
            # Create scatter plot
            os.chdir(original_dir)
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.set_facecolor('black')
            fig.patch.set_facecolor('black')
            
            # Plot sampled points
            x_points = [p['x'] for p in sample_points]
            y_points = [p['y'] for p in sample_points]
            r_points = [p['r'] for p in sample_points]
            
            scatter = ax.scatter(x_points, y_points, c=r_points, cmap='hot', 
                               s=30, alpha=0.8)
            plt.colorbar(scatter, ax=ax, label='Radius (M)')
            
            # Add photon sphere
            ax.plot(x_photon, y_photon, 'cyan', linewidth=2, alpha=0.5)
            
            ax.set_xlim(-max_lim, max_lim)
            ax.set_ylim(-max_lim, max_lim)
            ax.set_aspect('equal')
            ax.set_title('Sampled Points from Accretion Disk', color='white')
            
            output_path = "sampled_points_test.png"
            fig.savefig(output_path, dpi=150, facecolor='black', bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Saved sampled points to {output_path}")
        
        os.chdir(original_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        os.chdir(original_dir)

if __name__ == "__main__":
    print("🚀 Simple Luminet Test")
    print("=" * 40)
    
    create_simple_black_hole_image()
    
    print("\n" + "=" * 40)
    print("🏁 Test complete!")
    
    # List generated files
    for filename in ["simple_black_hole_test.png", "sampled_points_test.png"]:
        if os.path.exists(filename):
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Missing: {filename}")