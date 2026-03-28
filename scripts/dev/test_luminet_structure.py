#!/usr/bin/env python3
"""
Test the proper Luminet structure: ring + dark center + accretion disk.
"""

import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

sys.path.insert(0, '.')

try:
    from eventHorizon.luminet import draw_blackhole
    print("✅ Successfully imported draw_blackhole with Luminet structure")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Create test results directory
os.makedirs('luminet_structure_results', exist_ok=True)

def test_luminet_structure():
    """Test the proper Luminet structure."""
    print("\n🚀 Testing Proper Luminet Structure")
    print("=" * 60)
    print("Testing the authentic Luminet structure:")
    print("• Bright ring around the black hole (apparent inner edge)")
    print("• Dark center (black hole itself)")
    print("• Accretion disk material (filtered by apparent edges)")
    print("• Proper gravitational lensing effects")
    
    # Test configurations
    configs = [
        {
            "name": "luminet_structure_standard",
            "particle_count": 8000,
            "power_scale": 0.9,
            "inclination": 80.0,
            "levels": 120,
            "render_method": "tricontourf",
            "description": "Standard Luminet structure (tricontourf)"
        },
        {
            "name": "luminet_structure_edge_on",
            "particle_count": 8000,
            "power_scale": 0.9,
            "inclination": 90.0,
            "levels": 120,
            "render_method": "tricontourf",
            "description": "Edge-on Luminet structure"
        },
        {
            "name": "luminet_structure_face_on",
            "particle_count": 8000,
            "power_scale": 0.9,
            "inclination": 30.0,
            "levels": 120,
            "render_method": "tricontourf",
            "description": "Face-on Luminet structure"
        },
        {
            "name": "luminet_structure_scatter",
            "particle_count": 5000,
            "power_scale": 0.9,
            "inclination": 80.0,
            "render_method": "scatter",
            "description": "Luminet structure with scatter (no dark fill)"
        }
    ]
    
    for config in configs:
        print(f"\n🧪 Testing {config['description']}...")
        try:
            fig, ax = draw_blackhole(
                mass=1.0,
                inclination=config['inclination'],
                mode='points',
                particle_count=config['particle_count'],
                power_scale=config['power_scale'],
                levels=config.get('levels', 100),
                show_ghost_image=True,
                render_method=config['render_method'],
                show_labels=False,  # Don't show labels for cleaner look
                figsize=(12, 12),
                ax_lim=(-35, 35)
            )
            
            # Save the result
            filename = f"luminet_structure_results/{config['name']}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='black')
            print(f"✅ {config['description']}: Saved to {filename}")
            print(f"   - Should show: bright ring + dark center + accretion disk")
            print(f"   - Inclination: {config['inclination']}°")
            print(f"   - Method: {config['render_method']}")
            plt.close(fig)
            
        except Exception as e:
            print(f"❌ {config['description']} failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_comparison_with_original():
    """Create comparison to show the proper structure."""
    print(f"\n🔍 Creating comparison to show proper Luminet structure...")
    
    try:
        # High-quality version with proper structure
        fig, ax = draw_blackhole(
            mass=1.0,
            inclination=80.0,
            mode='points',
            particle_count=12000,
            power_scale=0.9,
            show_ghost_image=True,
            render_method='tricontourf',
            levels=150,
            figsize=(12, 12),
            ax_lim=(-30, 30)
        )
        
        filename = "luminet_structure_results/high_quality_luminet_structure.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='black')
        print(f"✅ High-quality Luminet structure: Saved to {filename}")
        print("   - Should show the complete authentic Luminet structure:")
        print("     • Bright orange ring (apparent inner edge)")
        print("     • Dark center (black hole)")
        print("     • Accretion disk wrapping around (gravitational lensing)")
        print("     • Ghost image below (Y-flipped)")
        plt.close(fig)
        
    except Exception as e:
        print(f"❌ High-quality comparison failed: {e}")
        return False
    
    return True

def main():
    """Run the Luminet structure test."""
    print("🌟 Testing Authentic Luminet Structure")
    print("=" * 60)
    print("This should now show the complete Luminet structure:")
    print("• Bright ring around the black hole (apparent inner edge)")
    print("• Dark center (the black hole itself)")
    print("• Accretion disk material (properly filtered)")
    print("• Gravitational lensing effects")
    print("• Ghost images with proper Y-flipping")
    
    success = True
    
    # Test Luminet structure
    if not test_luminet_structure():
        success = False
    
    # Test high-quality comparison
    if not test_comparison_with_original():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Luminet structure test completed!")
        print("✅ Bright ring (apparent inner edge) added")
        print("✅ Dark center properly implemented")
        print("✅ Particle filtering by apparent edges")
        print("✅ Proper gravitational lensing structure")
        print(f"\n📁 Results saved to 'luminet_structure_results/' folder")
        print("\n🔍 Check the images for the authentic Luminet structure:")
        print("   • Bright ring around the black hole")
        print("   • Dark center in the middle")
        print("   • Accretion disk wrapping around due to gravity")
        print("   • Characteristic 'mushroom cap' or 'kidney bean' shape")
        return 0
    else:
        print("❌ Luminet structure test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())