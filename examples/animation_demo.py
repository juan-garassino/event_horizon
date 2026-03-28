#!/usr/bin/env python3
"""
Animation and Multi-Inclination Demonstration

This script demonstrates the animation capabilities and multi-inclination
support in the eventHorizon framework.
"""

import matplotlib.pyplot as plt
import numpy as np
import eventHorizon
import os

def demonstrate_inclination_animation():
    """Demonstrate inclination sweep animation."""
    print("Inclination Animation Demonstration")
    print("=" * 40)
    
    # Create inclination sweep animation
    print("\n🎬 Creating inclination sweep animation...")
    animation_path = eventHorizon.create_inclination_movie(
        inclination_range=(30, 150),
        num_frames=24,
        quality_level="standard",
        output_format="gif",  # Use GIF for easier viewing
        particle_count=8000,
        power_scale=0.9
    )
    
    print(f"✅ Animation saved to: {animation_path}")
    return animation_path

def demonstrate_mass_evolution_animation():
    """Demonstrate mass evolution animation."""
    print("\nMass Evolution Animation Demonstration")
    print("=" * 45)
    
    # Create mass evolution animation
    print("\n🎬 Creating mass evolution animation...")
    animation_path = eventHorizon.create_mass_evolution_movie(
        mass_range=(0.5, 5.0),
        num_frames=20,
        quality_level="standard",
        output_format="gif",
        inclination=80.0,
        particle_count=6000
    )
    
    print(f"✅ Animation saved to: {animation_path}")
    return animation_path

def demonstrate_quality_evolution_animation():
    """Demonstrate quality evolution animation."""
    print("\nQuality Evolution Animation Demonstration")
    print("=" * 50)
    
    # Create quality evolution animation
    print("\n🎬 Creating quality evolution animation...")
    particle_counts = [1000, 2000, 5000, 10000, 20000, 35000]
    
    animation_path = eventHorizon.create_quality_evolution_movie(
        inclination=85.0,
        particle_counts=particle_counts,
        quality_level="standard",
        output_format="gif",
        power_scale=0.9
    )
    
    print(f"✅ Animation saved to: {animation_path}")
    return animation_path

def demonstrate_comparison_animation():
    """Demonstrate luminet vs traditional comparison animation."""
    print("\nComparison Animation Demonstration")
    print("=" * 40)
    
    # Create comparison animation
    print("\n🎬 Creating luminet vs traditional comparison...")
    animation_path = eventHorizon.create_luminet_vs_traditional_movie(
        inclination_range=(45, 135),
        num_frames=18,
        quality_level="standard",
        output_format="gif",
        particle_count=8000
    )
    
    print(f"✅ Animation saved to: {animation_path}")
    return animation_path

def demonstrate_multi_method_animation():
    """Demonstrate multi-method comparison animation."""
    print("\nMulti-Method Animation Demonstration")
    print("=" * 45)
    
    # Create multi-method comparison animation
    print("\n🎬 Creating multi-method comparison...")
    animation_path = eventHorizon.create_multi_method_comparison_movie(
        visualization_types=["luminet", "isoradials", "isoredshifts"],
        inclination_range=(60, 120),
        num_frames=15,
        quality_level="draft",  # Use draft for faster generation
        output_format="gif",
        particle_count=5000
    )
    
    print(f"✅ Animation saved to: {animation_path}")
    return animation_path

def demonstrate_parameter_sweep_animation():
    """Demonstrate parameter sweep animation."""
    print("\nParameter Sweep Animation Demonstration")
    print("=" * 50)
    
    # Create power scale sweep animation
    print("\n🎬 Creating power scale sweep animation...")
    power_scales = np.linspace(0.3, 1.5, 16)
    
    animation_path = eventHorizon.create_parameter_sweep_movie(
        parameter_name="power_scale",
        parameter_values=power_scales.tolist(),
        quality_level="standard",
        output_format="gif",
        inclination=80.0,
        particle_count=8000
    )
    
    print(f"✅ Animation saved to: {animation_path}")
    return animation_path

def demonstrate_multi_inclination_grid():
    """Demonstrate multi-inclination grid visualization."""
    print("\nMulti-Inclination Grid Demonstration")
    print("=" * 45)
    
    # Create multi-inclination grid
    print("\n🎯 Creating multi-inclination grid...")
    inclinations = [30, 45, 60, 75, 85, 90]
    
    fig, axes = eventHorizon.create_multi_inclination_grid(
        inclinations=inclinations,
        grid_size=(2, 3),
        quality_level="standard",
        particle_count=6000,
        power_scale=0.9
    )
    
    plt.suptitle('Black Hole Appearance at Different Inclination Angles', 
                color='white', fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig('results/examples/animation_demo/multi_inclination_grid.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig, axes

def demonstrate_parameter_comparison_grid():
    """Demonstrate parameter comparison grid."""
    print("\nParameter Comparison Grid Demonstration")
    print("=" * 50)
    
    # Create mass comparison grid
    print("\n🎯 Creating mass comparison grid...")
    masses = [0.5, 1.0, 2.0, 5.0]
    
    fig, axes = eventHorizon.create_parameter_comparison_grid(
        parameter_name="mass",
        parameter_values=masses,
        grid_size=(2, 2),
        quality_level="standard",
        inclination=80.0,
        particle_count=6000
    )
    
    plt.suptitle('Effect of Black Hole Mass on Appearance', 
                color='white', fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig('results/examples/animation_demo/mass_comparison_grid.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    # Create power scale comparison grid
    print("\n🎯 Creating power scale comparison grid...")
    power_scales = [0.3, 0.6, 0.9, 1.2]
    
    fig2, axes2 = eventHorizon.create_parameter_comparison_grid(
        parameter_name="power_scale",
        parameter_values=power_scales,
        grid_size=(2, 2),
        quality_level="standard",
        inclination=80.0,
        particle_count=8000
    )
    
    plt.suptitle('Effect of Power Scale on Brightness', 
                color='white', fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig('results/examples/animation_demo/power_scale_comparison_grid.png', 
                facecolor='black', dpi=200)
    plt.show()
    
    return fig2, axes2

def demonstrate_custom_animation_workflow():
    """Demonstrate custom animation workflow."""
    print("\nCustom Animation Workflow Demonstration")
    print("=" * 50)
    
    # Create custom parameter evolution
    print("\n🎬 Creating custom animation workflow...")
    
    # Define custom parameter evolution (sinusoidal inclination)
    num_frames = 30
    base_inclination = 80.0
    amplitude = 30.0
    
    inclinations = [
        base_inclination + amplitude * np.sin(2 * np.pi * i / num_frames)
        for i in range(num_frames)
    ]
    
    # Ensure inclinations are in valid range
    inclinations = [max(10, min(170, inc)) for inc in inclinations]
    
    animation_path = eventHorizon.create_parameter_sweep_movie(
        parameter_name="inclination",
        parameter_values=inclinations,
        quality_level="standard",
        output_format="gif",
        particle_count=8000,
        power_scale=0.9
    )
    
    print(f"✅ Custom animation saved to: {animation_path}")
    
    # Also create a plot showing the parameter evolution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(num_frames), inclinations, 'b-o', linewidth=2, markersize=6)
    ax.set_xlabel('Frame Number')
    ax.set_ylabel('Inclination Angle (degrees)')
    ax.set_title('Custom Inclination Evolution Pattern')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/examples/animation_demo/custom_parameter_evolution.png', dpi=150)
    plt.show()
    
    return animation_path

def demonstrate_animation_formats():
    """Demonstrate different animation output formats."""
    print("\nAnimation Format Demonstration")
    print("=" * 35)
    
    # Test different output formats
    formats = ["gif", "mp4", "frames"]
    results = {}
    
    for fmt in formats:
        print(f"\n🎬 Creating {fmt.upper()} format animation...")
        
        try:
            animation_path = eventHorizon.create_inclination_movie(
                inclination_range=(60, 120),
                num_frames=12,  # Fewer frames for demo
                quality_level="draft",  # Fast generation
                output_format=fmt,
                particle_count=3000,
                show_progress=False
            )
            
            results[fmt] = animation_path
            print(f"✅ {fmt.upper()} saved to: {animation_path}")
            
        except Exception as e:
            print(f"❌ {fmt.upper()} failed: {str(e)}")
            results[fmt] = None
    
    return results

def create_animation_summary():
    """Create summary of animation capabilities."""
    print("\nAnimation Capabilities Summary")
    print("=" * 35)
    
    capabilities = {
        "Inclination Sweep": "Animate viewing angle changes",
        "Mass Evolution": "Show effect of different black hole masses",
        "Quality Evolution": "Demonstrate particle count impact on quality",
        "Method Comparison": "Side-by-side comparison of visualization methods",
        "Parameter Sweep": "Animate any parameter evolution",
        "Multi-Inclination Grid": "Static grid showing multiple angles",
        "Parameter Grid": "Static grid comparing parameter values",
        "Custom Workflows": "User-defined parameter evolution patterns"
    }
    
    print("\n📋 Available Animation Types:")
    for capability, description in capabilities.items():
        print(f"   • {capability:20} | {description}")
    
    print("\n🎯 Supported Output Formats:")
    print("   • MP4     | High-quality video (requires ffmpeg)")
    print("   • GIF     | Animated GIF (requires Pillow)")
    print("   • Frames  | Individual PNG frames")
    
    print("\n⚙️  Quality Levels:")
    print("   • Draft        | Fast generation for previews")
    print("   • Standard     | Good balance of quality and speed")
    print("   • High         | High-quality for detailed analysis")
    print("   • Publication  | Maximum quality for publications")

def main():
    """Run all animation demonstrations."""
    print("EventHorizon Animation and Multi-Inclination Demo")
    print("=" * 55)
    
    # Create results directory
    os.makedirs('results/examples/animation_demo', exist_ok=True)
    os.makedirs('results/animations', exist_ok=True)
    
    # Run demonstrations
    try:
        inclination_anim = demonstrate_inclination_animation()
    except Exception as e:
        print(f"❌ Inclination animation failed: {e}")
        inclination_anim = None
    
    try:
        mass_anim = demonstrate_mass_evolution_animation()
    except Exception as e:
        print(f"❌ Mass evolution animation failed: {e}")
        mass_anim = None
    
    try:
        quality_anim = demonstrate_quality_evolution_animation()
    except Exception as e:
        print(f"❌ Quality evolution animation failed: {e}")
        quality_anim = None
    
    try:
        comparison_anim = demonstrate_comparison_animation()
    except Exception as e:
        print(f"❌ Comparison animation failed: {e}")
        comparison_anim = None
    
    try:
        multi_method_anim = demonstrate_multi_method_animation()
    except Exception as e:
        print(f"❌ Multi-method animation failed: {e}")
        multi_method_anim = None
    
    try:
        parameter_anim = demonstrate_parameter_sweep_animation()
    except Exception as e:
        print(f"❌ Parameter sweep animation failed: {e}")
        parameter_anim = None
    
    # Grid demonstrations (these should work even if animations fail)
    grid_results = demonstrate_multi_inclination_grid()
    param_grid_results = demonstrate_parameter_comparison_grid()
    
    try:
        custom_anim = demonstrate_custom_animation_workflow()
    except Exception as e:
        print(f"❌ Custom animation workflow failed: {e}")
        custom_anim = None
    
    try:
        format_results = demonstrate_animation_formats()
    except Exception as e:
        print(f"❌ Format demonstration failed: {e}")
        format_results = {}
    
    # Create summary
    create_animation_summary()
    
    print("\n" + "=" * 55)
    print("Animation Demo Completed!")
    print("Results saved to: results/examples/animation_demo/")
    print("Animations saved to: results/animations/")
    
    print("\nGenerated Files:")
    successful_animations = [
        ("Inclination Sweep", inclination_anim),
        ("Mass Evolution", mass_anim),
        ("Quality Evolution", quality_anim),
        ("Comparison", comparison_anim),
        ("Multi-Method", multi_method_anim),
        ("Parameter Sweep", parameter_anim),
        ("Custom Workflow", custom_anim)
    ]
    
    for name, path in successful_animations:
        if path:
            print(f"  ✅ {name:20} | {path}")
        else:
            print(f"  ❌ {name:20} | Failed to generate")
    
    print(f"\nFormat Test Results:")
    for fmt, path in format_results.items():
        if path:
            print(f"  ✅ {fmt.upper():8} | {path}")
        else:
            print(f"  ❌ {fmt.upper():8} | Failed")
    
    print("\nNote: Animation generation requires:")
    print("  • Pillow (pip install Pillow) for GIF output")
    print("  • FFmpeg (https://ffmpeg.org/) for MP4 output")

if __name__ == "__main__":
    main()