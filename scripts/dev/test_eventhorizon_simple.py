#!/usr/bin/env python3
"""
Simple EventHorizon Test - Test the current implementation
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def test_eventhorizon_functions():
    """Test the available EventHorizon functions."""
    
    print("🌌 Testing EventHorizon functions...")
    
    try:
        # Import EventHorizon functions
        from eventHorizon import quick_blackhole, draw_blackhole, plot_points
        
        print("✅ Successfully imported EventHorizon functions")
        
        # Test quick_blackhole function
        print("\n🚀 Testing quick_blackhole...")
        
        try:
            fig = quick_blackhole(
                mass=1.0,
                inclination_deg=60,
                save_path="eventhorizon_quick_test.png",
                show_plot=False
            )
            print("✅ quick_blackhole completed successfully")
            
        except Exception as e:
            print(f"❌ quick_blackhole failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test draw_blackhole function
        print("\n🎨 Testing draw_blackhole...")
        
        try:
            fig = draw_blackhole(
                mass=1.0,
                inclination_deg=60,
                disk_inner=6,
                disk_outer=20,
                n_points=500,
                save_path="eventhorizon_draw_test.png",
                show_plot=False
            )
            print("✅ draw_blackhole completed successfully")
            
        except Exception as e:
            print(f"❌ draw_blackhole failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_comparison_with_luminet():
    """Create a comparison between EventHorizon and Luminet."""
    
    print("\n🔬 Creating EventHorizon vs Luminet comparison...")
    
    # Test Luminet reference (we know this works)
    luminet_success = False
    try:
        sys.path.append('references/luminet/core')
        sys.path.append('references/luminet')
        
        from black_hole import BlackHole
        from bh_utils import polar_to_cartesian_lists
        from bh_math import calc_impact_parameter, redshift_factor, flux_observed
        
        original_dir = os.getcwd()
        os.chdir('references/luminet')
        
        # Create Luminet visualization
        bh = BlackHole(inclination=60, mass=1.0)
        bh.disk_outer_edge = 20.0
        bh.disk_inner_edge = 6.0
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        # Sample points
        sample_data = []
        n_points = 200
        
        for i in range(n_points):
            r = bh.disk_inner_edge + (bh.disk_outer_edge - bh.disk_inner_edge) * np.random.random()
            theta = np.random.random() * 2 * np.pi
            
            try:
                b = calc_impact_parameter(r, bh.t, theta, bh.M,
                                        midpoint_iterations=8,
                                        initial_guesses=6,
                                        min_periastron=3.1*bh.M)
                
                if b is not None and b > 0:
                    x, y = polar_to_cartesian_lists([b], [theta], rotation=-np.pi/2)
                    z_factor = redshift_factor(r, theta, bh.t, bh.M, b)
                    flux = flux_observed(r, bh.acc, bh.M, z_factor)
                    
                    sample_data.append({
                        'X': x[0], 'Y': y[0], 
                        'flux_o': flux
                    })
            except:
                continue
        
        if len(sample_data) > 10:
            x_vals = [p['X'] for p in sample_data]
            y_vals = [p['Y'] for p in sample_data]
            flux_vals = [p['flux_o'] for p in sample_data]
            
            flux_vals = np.array(flux_vals)
            flux_vals = (flux_vals - flux_vals.min()) / (flux_vals.max() - flux_vals.min())
            
            scatter = ax.scatter(x_vals, y_vals, c=flux_vals, cmap='hot', 
                               s=20, alpha=0.8)
            
            # Add photon sphere
            theta_circle = np.linspace(0, 2*np.pi, 100)
            x_photon = bh.critical_b * np.cos(theta_circle)
            y_photon = bh.critical_b * np.sin(theta_circle)
            ax.plot(x_photon, y_photon, 'cyan', linewidth=2, alpha=0.7)
            
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
            ax.set_aspect('equal')
            ax.set_title('Luminet Reference\n(M=1.0, incl=60°)', color='white', fontsize=14)
            
            os.chdir(original_dir)
            fig.savefig("luminet_comparison_test.png", dpi=150, facecolor='black', bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Luminet reference created with {len(sample_data)} points")
            luminet_success = True
        else:
            os.chdir(original_dir)
            
    except Exception as e:
        print(f"❌ Luminet comparison failed: {e}")
        os.chdir(original_dir)
    
    # Create side-by-side if both exist
    eh_files = ["eventhorizon_quick_test.png", "eventhorizon_draw_test.png"]
    luminet_file = "luminet_comparison_test.png"
    
    for eh_file in eh_files:
        if os.path.exists(eh_file) and os.path.exists(luminet_file):
            try:
                import matplotlib.image as mpimg
                
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
                fig.patch.set_facecolor('black')
                
                # EventHorizon
                eh_img = mpimg.imread(eh_file)
                ax1.imshow(eh_img)
                ax1.set_title(f"EventHorizon\n({eh_file})", color='white', fontsize=14)
                ax1.axis('off')
                
                # Luminet
                luminet_img = mpimg.imread(luminet_file)
                ax2.imshow(luminet_img)
                ax2.set_title("Luminet Reference", color='white', fontsize=14)
                ax2.axis('off')
                
                plt.tight_layout()
                comparison_name = f"comparison_{eh_file.replace('.png', '')}.png"
                fig.savefig(comparison_name, dpi=150, facecolor='black', bbox_inches='tight')
                plt.close(fig)
                
                print(f"✅ Created comparison: {comparison_name}")
                
            except Exception as e:
                print(f"❌ Failed to create comparison for {eh_file}: {e}")

def main():
    """Main test function."""
    
    print("🔬 EventHorizon Simple Test")
    print("=" * 40)
    
    # Test EventHorizon functions
    eh_success = test_eventhorizon_functions()
    
    # Create comparison with Luminet
    create_comparison_with_luminet()
    
    print("\n" + "=" * 40)
    print("🏁 Test complete!")
    
    # List generated files
    possible_files = [
        "eventhorizon_quick_test.png",
        "eventhorizon_draw_test.png", 
        "luminet_comparison_test.png",
        "comparison_eventhorizon_quick_test.png",
        "comparison_eventhorizon_draw_test.png"
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    main()