#!/usr/bin/env python3
"""
Compare EventHorizon vs Luminet Reference Implementation

This script creates visualizations from both implementations to compare
their outputs and identify differences.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def test_eventhorizon():
    """Test the current EventHorizon implementation."""
    
    print("🌌 Testing EventHorizon implementation...")
    
    try:
        # Import EventHorizon functions
        from eventHorizon import draw_blackhole, VisualizationModel, get_default_config
        
        print(f"✅ EventHorizon imported successfully")
        
        # Create visualization using draw_blackhole
        fig, ax = draw_blackhole(
            mass=1.0,
            inclination=60.0,
            mode='points',
            particle_count=500,
            figsize=(8, 8),
            ax_lim=(-15, 15),
            show_ghost_image=True
        )
        
        print(f"✅ EventHorizon visualization created: M=1.0, incl=60°")
        
        # Save the figure
        fig.savefig("eventhorizon_test.png", dpi=150, facecolor='black', bbox_inches='tight')
        plt.close(fig)
        
        print("✅ EventHorizon visualization saved to eventhorizon_test.png")
        
        # Create a model to get sample data for comparison
        config = get_default_config()
        config.mass = 1.0
        config.inclination_deg = 60.0
        config.disk_inner = 6.0
        config.disk_outer = 20.0
        
        model = VisualizationModel(config)
        sample_data = model.generate_particles(n_particles=100)
        
        print(f"   Sample data shape: {sample_data.shape}")
        print(f"   Columns: {list(sample_data.columns)}")
        
        return True, sample_data
        
    except Exception as e:
        print(f"❌ EventHorizon test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_luminet_reference():
    """Test the Luminet reference implementation."""
    
    print("\n🔭 Testing Luminet reference implementation...")
    
    try:
        # Add reference paths
        sys.path.append('references/luminet/core')
        sys.path.append('references/luminet')
        
        from black_hole import BlackHole
        from bh_utils import polar_to_cartesian_lists
        from bh_math import calc_impact_parameter
        
        # Change to luminet directory
        original_dir = os.getcwd()
        os.chdir('references/luminet')
        
        # Create BlackHole with matching parameters
        bh = BlackHole(inclination=60, mass=1.0)
        bh.disk_outer_edge = 20.0
        bh.disk_inner_edge = 6.0
        
        print(f"✅ Luminet BlackHole created: M={bh.M}, incl={bh.t*180/np.pi:.0f}°")
        print(f"   Disk: {bh.disk_inner_edge} to {bh.disk_outer_edge}")
        
        # Create manual visualization similar to EventHorizon
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        # Sample points manually
        sample_data = []
        n_points = 100
        
        for i in range(n_points):
            # Biased sampling like Luminet
            r = bh.disk_inner_edge + (bh.disk_outer_edge - bh.disk_inner_edge) * np.random.random()
            theta = np.random.random() * 2 * np.pi
            
            try:
                # Calculate impact parameter (direct image)
                b = calc_impact_parameter(r, bh.t, theta, bh.M,
                                        midpoint_iterations=10,
                                        initial_guesses=8,
                                        min_periastron=3.1*bh.M)
                
                if b is not None and b > 0:
                    # Apply critical -π/2 rotation
                    x, y = polar_to_cartesian_lists([b], [theta], rotation=-np.pi/2)
                    
                    # Calculate redshift factor
                    from bh_math import redshift_factor, flux_observed
                    z_factor = redshift_factor(r, theta, bh.t, bh.M, b)
                    flux = flux_observed(r, bh.acc, bh.M, z_factor)
                    
                    sample_data.append({
                        'X': x[0], 'Y': y[0], 
                        'impact_parameter': b,
                        'angle': theta,
                        'z_factor': z_factor,
                        'flux_o': flux,
                        'radius': r
                    })
            except:
                continue
        
        print(f"   Sampled {len(sample_data)} points successfully")
        
        if len(sample_data) > 10:
            # Create scatter plot
            x_vals = [p['X'] for p in sample_data]
            y_vals = [p['Y'] for p in sample_data]
            flux_vals = [p['flux_o'] for p in sample_data]
            
            # Normalize flux for visualization
            flux_vals = np.array(flux_vals)
            flux_vals = (flux_vals - flux_vals.min()) / (flux_vals.max() - flux_vals.min())
            
            scatter = ax.scatter(x_vals, y_vals, c=flux_vals, cmap='hot', 
                               s=30, alpha=0.8)
            plt.colorbar(scatter, ax=ax, label='Normalized Flux')
            
            # Add photon sphere
            theta_circle = np.linspace(0, 2*np.pi, 100)
            x_photon = bh.critical_b * np.cos(theta_circle)
            y_photon = bh.critical_b * np.sin(theta_circle)
            ax.plot(x_photon, y_photon, 'cyan', linewidth=2, alpha=0.5, label='Photon Sphere')
            
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
            ax.set_aspect('equal')
            ax.set_title('Luminet Reference Implementation', color='white')
            ax.legend()
            
            os.chdir(original_dir)
            fig.savefig("luminet_reference_test.png", dpi=150, facecolor='black', bbox_inches='tight')
            plt.close(fig)
            
            print("✅ Luminet reference visualization saved to luminet_reference_test.png")
            
            # Convert to DataFrame-like structure for comparison
            import pandas as pd
            df = pd.DataFrame(sample_data)
            
            return True, df
        else:
            os.chdir(original_dir)
            return False, None
            
    except Exception as e:
        print(f"❌ Luminet reference test failed: {e}")
        import traceback
        traceback.print_exc()
        os.chdir(original_dir)
        return False, None

def compare_data(eh_data, luminet_data):
    """Compare the data structures and values between implementations."""
    
    print("\n📊 Comparing data structures...")
    
    if eh_data is not None and luminet_data is not None:
        print("EventHorizon columns:", list(eh_data.columns))
        print("Luminet columns:", list(luminet_data.columns))
        
        # Check coordinate ranges
        if 'X' in eh_data.columns and 'X' in luminet_data.columns:
            print(f"\nCoordinate ranges:")
            print(f"EventHorizon X: [{eh_data['X'].min():.2f}, {eh_data['X'].max():.2f}]")
            print(f"EventHorizon Y: [{eh_data['Y'].min():.2f}, {eh_data['Y'].max():.2f}]")
            print(f"Luminet X: [{luminet_data['X'].min():.2f}, {luminet_data['X'].max():.2f}]")
            print(f"Luminet Y: [{luminet_data['Y'].min():.2f}, {luminet_data['Y'].max():.2f}]")
        
        # Check if impact parameter exists
        eh_has_b = 'impact_parameter' in eh_data.columns or 'b' in eh_data.columns
        luminet_has_b = 'impact_parameter' in luminet_data.columns
        
        print(f"\nImpact parameter:")
        print(f"EventHorizon has impact parameter: {eh_has_b}")
        print(f"Luminet has impact parameter: {luminet_has_b}")
        
        if eh_has_b and luminet_has_b:
            eh_b_col = 'impact_parameter' if 'impact_parameter' in eh_data.columns else 'b'
            print(f"EventHorizon b range: [{eh_data[eh_b_col].min():.2f}, {eh_data[eh_b_col].max():.2f}]")
            print(f"Luminet b range: [{luminet_data['impact_parameter'].min():.2f}, {luminet_data['impact_parameter'].max():.2f}]")
    
    else:
        print("❌ Cannot compare - one or both datasets missing")

def create_side_by_side_comparison():
    """Create a side-by-side comparison plot."""
    
    print("\n🖼️ Creating side-by-side comparison...")
    
    # Check if both images exist
    eh_exists = os.path.exists("eventhorizon_test.png")
    luminet_exists = os.path.exists("luminet_reference_test.png")
    
    if eh_exists and luminet_exists:
        import matplotlib.image as mpimg
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.patch.set_facecolor('black')
        
        # Load and display EventHorizon image
        eh_img = mpimg.imread("eventhorizon_test.png")
        ax1.imshow(eh_img)
        ax1.set_title("EventHorizon Implementation", color='white', fontsize=14)
        ax1.axis('off')
        
        # Load and display Luminet image
        luminet_img = mpimg.imread("luminet_reference_test.png")
        ax2.imshow(luminet_img)
        ax2.set_title("Luminet Reference Implementation", color='white', fontsize=14)
        ax2.axis('off')
        
        plt.tight_layout()
        fig.savefig("implementation_comparison.png", dpi=150, facecolor='black', bbox_inches='tight')
        plt.close(fig)
        
        print("✅ Side-by-side comparison saved to implementation_comparison.png")
    else:
        print(f"❌ Cannot create comparison - missing images (EH: {eh_exists}, Luminet: {luminet_exists})")

def main():
    """Main comparison function."""
    
    print("🔬 Implementation Comparison Test")
    print("=" * 50)
    
    # Test both implementations
    eh_success, eh_data = test_eventhorizon()
    luminet_success, luminet_data = test_luminet_reference()
    
    # Compare data if both succeeded
    if eh_success and luminet_success:
        compare_data(eh_data, luminet_data)
    
    # Create visual comparison
    create_side_by_side_comparison()
    
    print("\n" + "=" * 50)
    print("🏁 Comparison complete!")
    
    # List all generated files
    files = ["eventhorizon_test.png", "luminet_reference_test.png", "implementation_comparison.png"]
    for filename in files:
        if os.path.exists(filename):
            print(f"✅ Generated: {filename}")
        else:
            print(f"❌ Missing: {filename}")

if __name__ == "__main__":
    main()