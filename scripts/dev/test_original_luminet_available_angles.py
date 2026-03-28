#!/usr/bin/env python3
"""Test the original Luminet implementation using available angle data."""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def test_original_luminet_available():
    """Test the original Luminet implementation using available CSV files."""
    print("🚀 Testing Original Luminet Implementation (Available Angles)")
    print("=" * 60)
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to the luminet directory
        luminet_dir = os.path.join(original_dir, 'references', 'luminet')
        os.chdir(luminet_dir)
        print(f"Changed to directory: {luminet_dir}")
        
        # Add the core directory to Python path
        sys.path.insert(0, 'core')
        
        # Import the original Luminet classes
        from black_hole import BlackHole
        print("✅ Successfully imported original BlackHole class")
        
        # Test available inclination angles (based on existing CSV files)
        available_angles = [29, 59, 80, 90]
        
        for inclination in available_angles:
            print(f"\nTesting inclination {inclination}°...")
            
            # Create a BlackHole instance
            bh = BlackHole(mass=1.0, inclination=inclination)
            actual_inclination = bh.t * 180/np.pi
            actual_inclination_int = int(round(bh.t * 180 / np.pi))
            print(f"✅ Created BlackHole: mass={bh.M}, inclination={actual_inclination:.1f}° (file suffix: {actual_inclination_int})")
            
            # Check if CSV files exist
            expected_file1 = f"Points/points_incl={actual_inclination_int}.csv"
            expected_file2 = f"Points/points_secondary_incl={actual_inclination_int}.csv"
            print(f"  Expected files: {expected_file1}, {expected_file2}")
            
            if os.path.exists(expected_file1) and os.path.exists(expected_file2):
                print("  ✅ CSV files found")
                
                # Create plot using existing data
                print(f"  Creating plot using existing data...")
                try:
                    fig, ax = bh.plot_points(power_scale=0.9, levels=50)
                    print("  ✅ Successfully created plot")
                    
                    # Save the plot
                    output_path = os.path.join(original_dir, f'original_luminet_incl_{inclination}.png')
                    fig.savefig(output_path, dpi=300, facecolor='black', bbox_inches='tight')
                    print(f"  ✅ Saved plot to: original_luminet_incl_{inclination}.png")
                    plt.close(fig)
                    
                except Exception as e:
                    print(f"    ⚠️  Plot creation issue: {e}")
                    print(f"    Skipping plot for inclination {inclination}°")
                    continue
            else:
                print(f"  ⚠️  CSV files missing, sampling new points...")
                
                # Sample points for this inclination
                try:
                    bh.sample_points(n_points=2000)
                    print("  ✅ Successfully sampled points")
                    
                    # Try to create plot
                    fig, ax = bh.plot_points(power_scale=0.9, levels=50)
                    print("  ✅ Successfully created plot")
                    
                    # Save the plot
                    output_path = os.path.join(original_dir, f'original_luminet_incl_{inclination}.png')
                    fig.savefig(output_path, dpi=300, facecolor='black', bbox_inches='tight')
                    print(f"  ✅ Saved plot to: original_luminet_incl_{inclination}.png")
                    plt.close(fig)
                    
                except Exception as e:
                    print(f"    ⚠️  Sampling/plotting failed: {e}")
                    continue
        
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

def create_original_luminet_30_60():
    """Create original Luminet data for 30° and 60° inclinations."""
    print("\n🔧 Creating Original Luminet Data for 30° and 60°")
    print("=" * 60)
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to the luminet directory
        luminet_dir = os.path.join(original_dir, 'references', 'luminet')
        os.chdir(luminet_dir)
        
        # Add the core directory to Python path
        sys.path.insert(0, 'core')
        
        # Import the original Luminet classes
        from black_hole import BlackHole
        
        # Create data for 30° and 60°
        target_angles = [30, 60]
        
        for inclination in target_angles:
            print(f"\nCreating data for inclination {inclination}°...")
            
            try:
                # Create a BlackHole instance
                bh = BlackHole(mass=1.0, inclination=inclination)
                actual_inclination_int = int(round(bh.t * 180 / np.pi))
                print(f"✅ Created BlackHole for {inclination}° (file suffix: {actual_inclination_int})")
                
                # Sample points (use smaller number for faster generation)
                print(f"  Sampling 1500 points...")
                bh.sample_points(n_points=1500)
                print("  ✅ Successfully sampled points")
                
                # Create plot
                print(f"  Creating plot...")
                fig, ax = bh.plot_points(power_scale=0.9, levels=50)
                print("  ✅ Successfully created plot")
                
                # Save the plot
                output_path = os.path.join(original_dir, f'original_luminet_incl_{inclination}.png')
                fig.savefig(output_path, dpi=300, facecolor='black', bbox_inches='tight')
                print(f"  ✅ Saved plot to: original_luminet_incl_{inclination}.png")
                plt.close(fig)
                
            except Exception as e:
                print(f"    ❌ Failed to create data for {inclination}°: {e}")
                continue
        
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

def create_inclination_comparison():
    """Create a comparison of different inclination angles."""
    print("\n📊 Creating Inclination Comparison...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    # Images to compare
    images = [
        ('original_luminet_incl_30.png', 'Original Luminet 30°\n(Face-on)'),
        ('original_luminet_incl_60.png', 'Original Luminet 60°\n(Intermediate)'),
        ('original_luminet_incl_80.png', 'Original Luminet 80°\n(Nearly Edge-on)'),
        ('original_luminet_incl_90.png', 'Original Luminet 90°\n(Edge-on)')
    ]
    
    for i, (filename, title) in enumerate(images):
        row = i // 2
        col = i % 2
        ax = axes[row, col]
        
        try:
            import matplotlib.image as mpimg
            img = mpimg.imread(filename)
            ax.imshow(img)
            ax.set_title(title, color='white', fontsize=14, pad=10)
            ax.axis('off')
            print(f"✅ Loaded {filename}")
        except Exception as e:
            ax.text(0.5, 0.5, f'{title}\nNot Available', 
                   ha='center', va='center', color='white', fontsize=12)
            ax.set_facecolor('black')
            ax.set_title(title, color='white', fontsize=14)
            print(f"⚠️  Could not load {filename}: {e}")
    
    plt.tight_layout()
    fig.savefig('original_luminet_inclination_comparison.png', dpi=300, facecolor='black', bbox_inches='tight')
    print("✅ Inclination comparison saved as: original_luminet_inclination_comparison.png")
    plt.close(fig)

def main():
    """Main test function."""
    print("🎯 Testing Original Luminet at Multiple Inclinations")
    print("=" * 70)
    print("This will test the original Luminet implementation at different")
    print("inclination angles to understand the proper black hole structure.")
    print("=" * 70)
    
    # Test available angles first
    success1 = test_original_luminet_available()
    
    # Create missing 30° and 60° data
    success2 = create_original_luminet_30_60()
    
    if success1 or success2:
        # Create comparison
        create_inclination_comparison()
        
        print("\n" + "=" * 70)
        print("✅ Original Luminet multi-inclination test completed!")
        print("📊 Check 'original_luminet_inclination_comparison.png' for results")
        print("🎯 This shows how the black hole structure changes with inclination")
        print("=" * 70)
        
        return 0
    else:
        print("\n❌ Original Luminet test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())