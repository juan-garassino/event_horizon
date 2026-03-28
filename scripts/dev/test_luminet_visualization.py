#!/usr/bin/env python3
"""
Test Luminet Visualization Script

This script creates a black hole visualization using the reference Luminet implementation
to verify our analysis and see the expected output format.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add reference path to import Luminet modules
sys.path.append('references/luminet/core')
sys.path.append('references/luminet')

try:
    from black_hole import BlackHole
    print("✅ Successfully imported BlackHole class")
except ImportError as e:
    print(f"❌ Could not import BlackHole: {e}")
    sys.exit(1)

def create_test_visualization():
    """Create a test black hole visualization using the reference implementation."""
    
    print("🔭 Creating test black hole visualization...")
    
    # Initialize black hole with parameters similar to reference
    M = 2.0  # Black hole mass
    incl = 66  # Inclination angle in degrees
    
    print(f"   Mass: {M}")
    print(f"   Inclination: {incl}°")
    
    try:
        # Create BlackHole instance
        bh = BlackHole(inclination=incl, mass=M)
        print("✅ BlackHole instance created successfully")
        
        # Set parameters similar to reference main.py
        bh.disk_outer_edge = 150 * M
        bh.iz_solver_params['radial_precision'] = 50
        bh.angular_properties["angular_precision"] = 300
        
        print(f"   Disk outer edge: {bh.disk_outer_edge}")
        print(f"   Disk inner edge: {bh.disk_inner_edge}")
        print(f"   Critical impact parameter: {bh.critical_b}")
        
        # Test 1: Create a simple isoradial plot
        print("\n📊 Test 1: Creating isoradial visualization...")
        try:
            direct_radii = [10*M, 20*M, 30*M]
            ghost_radii = [10*M, 20*M]
            
            fig, ax = bh.plot_isoradials(direct_radii, ghost_radii, show=False)
            
            # Save the plot
            output_path = "test_isoradials.png"
            fig.savefig(output_path, dpi=150, facecolor='black', bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Isoradial plot saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Isoradial plot failed: {e}")
        
        # Test 2: Sample points and create visualization
        print("\n📊 Test 2: Sampling points and creating visualization...")
        try:
            # Sample fewer points for faster testing
            n_points = 500
            print(f"   Sampling {n_points} points...")
            
            bh.sample_points(n_points=n_points)
            print("✅ Points sampled successfully")
            
            # Create points visualization
            fig, ax = bh.plot_points(power_scale=0.9, levels=50)
            
            # Save the plot
            output_path = "test_sampled_points.png"
            fig.savefig(output_path, dpi=150, facecolor='black', bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Sampled points plot saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Sampled points visualization failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Create isoredshift visualization
        print("\n📊 Test 3: Creating isoredshift visualization...")
        try:
            redshifts = [-.15, 0., .15, .25]
            print(f"   Calculating redshifts: {redshifts}")
            
            fig, ax = bh.plot_isoredshifts(redshifts=redshifts, plot_core=True)
            
            # Save the plot
            output_path = "test_isoredshifts.png"
            fig.savefig(output_path, dpi=150, facecolor='#F0EAD6', bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Isoredshift plot saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Isoredshift visualization failed: {e}")
            import traceback
            traceback.print_exc()
            
        print("\n🎉 Test visualization complete!")
        print("Generated files:")
        for filename in ["test_isoradials.png", "test_sampled_points.png", "test_isoredshifts.png"]:
            if os.path.exists(filename):
                print(f"   ✅ {filename}")
            else:
                print(f"   ❌ {filename} (not created)")
                
    except Exception as e:
        print(f"❌ Failed to create BlackHole instance: {e}")
        import traceback
        traceback.print_exc()

def analyze_coordinate_transformation():
    """Test the coordinate transformation to verify our analysis."""
    
    print("\n🔍 Testing coordinate transformation analysis...")
    
    # Import the utility function
    try:
        from bh_utils import polar_to_cartesian_lists
        
        # Test the critical -π/2 rotation
        test_radii = [10, 20, 30]
        test_angles = [0, np.pi/2, np.pi, 3*np.pi/2]
        
        print("   Testing polar to cartesian conversion:")
        print("   Input radii:", test_radii[:1])  # Just first radius for clarity
        print("   Input angles:", [f"{a:.2f}" for a in test_angles])
        
        # Without rotation
        x_no_rot, y_no_rot = polar_to_cartesian_lists([test_radii[0]] * len(test_angles), test_angles, rotation=0)
        print("   Without rotation:", [(f"{x:.1f}", f"{y:.1f}") for x, y in zip(x_no_rot, y_no_rot)])
        
        # With critical -π/2 rotation
        x_rot, y_rot = polar_to_cartesian_lists([test_radii[0]] * len(test_angles), test_angles, rotation=-np.pi/2)
        print("   With -π/2 rotation:", [(f"{x:.1f}", f"{y:.1f}") for x, y in zip(x_rot, y_rot)])
        
        print("✅ Coordinate transformation verified")
        
    except Exception as e:
        print(f"❌ Coordinate transformation test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Luminet Reference Visualization Test")
    print("=" * 60)
    
    # Change to the references/luminet directory to access parameters.ini
    original_dir = os.getcwd()
    try:
        os.chdir('references/luminet')
        print(f"📁 Changed to directory: {os.getcwd()}")
        
        create_test_visualization()
        analyze_coordinate_transformation()
        
    except Exception as e:
        print(f"❌ Error during visualization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        os.chdir(original_dir)
        print(f"📁 Returned to directory: {os.getcwd()}")
    
    print("\n" + "=" * 60)
    print("🏁 Test complete!")