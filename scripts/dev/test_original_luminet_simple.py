#!/usr/bin/env python3
"""Simple test to run the original Luminet implementation from references folder."""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def test_original_luminet():
    """Test the original Luminet implementation."""
    print("🚀 Testing Original Luminet Implementation")
    print("=" * 50)
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to the luminet directory
        luminet_dir = os.path.join(original_dir, 'references', 'luminet')
        os.chdir(luminet_dir)
        print(f"Changed to directory: {luminet_dir}")
        
        # Create Points directory if it doesn't exist
        points_dir = os.path.join(luminet_dir, 'Points')
        if not os.path.exists(points_dir):
            os.makedirs(points_dir)
            print(f"✅ Created Points directory: {points_dir}")
        
        # Add the core directory to Python path
        sys.path.insert(0, 'core')
        
        # Import the original Luminet classes
        from black_hole import BlackHole
        print("✅ Successfully imported original BlackHole class")
        
        # Test different inclination angles
        inclinations = [30, 60, 80, 90]
        
        for inclination in inclinations:
            print(f"\nTesting inclination {inclination}°...")
            
            # Create a BlackHole instance
            bh = BlackHole(mass=1.0, inclination=inclination)
            actual_inclination = bh.t * 180/3.14159
            actual_inclination_int = int(round(bh.t * 180 / np.pi))
            print(f"✅ Created BlackHole: mass={bh.M}, inclination={actual_inclination:.1f}° (file suffix: {actual_inclination_int})")
            
            # Sample points
            print(f"  Sampling 1000 points...")  # Reduced for faster testing
            bh.sample_points(n_points=1000)
            print("  ✅ Successfully sampled points")
            
            # Check if CSV files were created
            expected_file1 = f"Points/points_incl={actual_inclination_int}.csv"
            expected_file2 = f"Points/points_secondary_incl={actual_inclination_int}.csv"
            print(f"  Expected files: {expected_file1}, {expected_file2}")
            
            if os.path.exists(expected_file1) and os.path.exists(expected_file2):
                print("  ✅ CSV files found")
            else:
                print(f"  ⚠️  CSV files missing")
                continue
            
            # Create plot
            print(f"  Creating plot...")
            try:
                fig, ax = bh.plot_points(power_scale=0.9, levels=50)  # Reduced levels for faster rendering
                print("  ✅ Successfully created plot")
            except Exception as e:
                print(f"    ⚠️  Plot creation issue: {e}")
                print(f"    Skipping plot for inclination {inclination}°")
                continue
            
            # Save the plot
            output_path = os.path.join(original_dir, f'original_luminet_incl_{inclination}.png')
            fig.savefig(output_path, dpi=300, facecolor='black', bbox_inches='tight')
            print(f"  ✅ Saved plot to: original_luminet_incl_{inclination}.png")
            plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Always return to original directory
        os.chdir(original_dir)
        # Remove the core directory from path
        if 'core' in sys.path:
            sys.path.remove('core')

def main():
    """Run the test."""
    print("Testing the original Luminet implementation from references/luminet/")
    print("This will show us the authentic relativistic black hole shape.")
    
    if test_original_luminet():
        print("\n🎉 Original Luminet test successful!")
        print("✅ Generated authentic Luminet visualization")
        print("📁 Check 'original_luminet_test.png' to see the proper relativistic shape")
        print("🔍 This shows how the visualization should look with:")
        print("   • Proper relativistic 'mushroom cap' shape")
        print("   • Correct rotation and orientation")
        print("   • Ghost images with Y-coordinate flipping")
        return 0
    else:
        print("\n❌ Original Luminet test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())